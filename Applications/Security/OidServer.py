
import cherrypy
import openid
from openid.server import server
from openid.store.filestore import FileOpenIDStore
from openid.store.memstore import MemoryStore
from WMCore.WebTools import cms_sreg as sreg
from openid.consumer import discover
import cgi # to use escape()
import urllib # to use urlencode()
try:
    # Python 2.6
    import json
except:
    # Prior to 2.6 requires simplejson
    import simplejson as json
from WMCore.WebTools.Page import Page # for printing messages
from WMCore.WMFactory import WMFactory
from DBOidStore import DBOidStore

SESSION_NAME = 'SecurityModuleServer'

class OidServer(Page):
    def __init__(self, config):
        self.config = config # Saves the config because Page needs it
        self.encoder = json.JSONEncoder()
        
        # The full URL of this openid server
        if hasattr(config,'server_url'):
            self.base_path = '%s/' % config.server_url
        else:
            self.base_path = '%s/' % cherrypy.url()

        # Now instantiates the OpenID Store (used for nonces and associations)
        if config.store == 'filestore':
            store = FileOpenIDStore(config.store_path)
        elif config.store == 'dbstore':
            store = DBOidStore(config.store_source)
        else:
            store = MemoryStore()
                    
        # Now instantiates the OpenID server
        self.openid = server.Server(store, self.base_path + 'openidserver')

        # Record how to get user details out...
        factory = WMFactory('oid_factory')
        self.userstore = factory.loadObject(config.users_store.object, 
                                            config.users_store)

        # List of remote sites allowed to request auth/authz to this server
        self.truststore = factory.loadObject(config.trust_store.object,
                                             config.trust_store)
        
        # This is a thread safe object to display web pages/forms related to 
        # the oid server. I put it on a separate class to avoid blowing
        # the main class with html code.
        self.webpages = OidServerWebPages()

        # *** Should enable cherrypy session somewhere... sorry
        cherrypy.config.update({'tools.sessions.on': True,
                                'tools.sessions.storage_type': 'ram',
                                #'tools.sessions.storage_type': "file",
                                #'tools.sessions.storage_path': "/tmp/oidserver-sessions",
                                'tools.sessions.timeout': 60,
                                'tools.sessions.name': 'oidserver_sid'})
                                
        #self.session_name = getattr(config, 'session_name', SESSION_NAME)

    # The index page only shows information about this OpenID server
    @cherrypy.expose
    def index(self, *args, **kwargs):
        return self.webpages.showMainPage(self.base_path)

    # Displays a page with a form to get the login name of the user
    @cherrypy.expose
    def login(self):
        return self.webpages.showLoginPage(self.base_path, self.base_path,
                                           self.base_path)

    @cherrypy.expose
    def loginsubmit(self,submit='cancel', identifier=None, password=None,
                    fail_to=None, success_to=None):
        """
        Handles the login form submission.

        A logout is performed by a login request with identifier=None
        """
        if submit == 'login':
            sessuser = get_username()
            if sessuser and identifier and identifier != sessuser:
                set_username(None) # logout the user first
                # Then resend the login request to generate another session
                raise cherrypy.HTTPRedirect(self.base_path +
                                            "loginsubmit?" +
                                            urllib.urlencode(cherrypy.request.params))
            if identifier is None or self.checkAuth(identifier, password):
                set_username(identifier)
                raise cherrypy.HTTPRedirect(success_to or self.base_path)
            
        # If it is not a login, it will work as a cancel request
        raise cherrypy.HTTPRedirect(fail_to or self.base_path)

    @cherrypy.expose
    def openidserver(self,*args,**kwargs):
        """
        This is the endpoint server: the main handler for openid requests
        """
        try:
            # Transforms the web request parameters into an openid request
            oidrequest = self.openid.decodeRequest(cherrypy.request.params)
        except server.ProtocolError, why:
            return self.displayOidResponse(why)

        if oidrequest is None:
            # Display text indicating that this is an endpoint.
            return self.webpages.showAboutPage(self.base_path)
        if oidrequest.mode in ["checkid_immediate", "checkid_setup"]:
            # Ok. This is an CheckID request. This means that we need to
            # assert that the identity the user is claiming belongs to him
            # (we need to authenticate the user based on a password or on his
            # certificate). After authenticating the user, we also need to ask
            # him if he trusts the consumer site which is requesting his id
            # information
            return self.handleCheckIDRequest(oidrequest)
        else:
            # It is not a CheckID request. So let the openid handle it and
            # decide what to do. According to openid documentation, these
            # requests are related to establishing associations between
            # client and server and verifying authenticity of previous
            # communications.
            oidresponse = self.openid.handleRequest(oidrequest)
            return self.displayOidResponse(oidresponse)

    def displayOidResponse(self, oidresponse):
        """Formats the oid response into HTTP and send it to the user browser"""
        try:
            # Transforms an Openid response into a web response (and signs it)
            webresp = self.openid.encodeResponse(oidresponse)
        except server.EncodingError, why:
            text = why.response.encodeToKVForm()
            return self.webpages.showErrorPage('<pre>%s</pre>' % cgi.escape(text))
 
        # Now it sends the web response to the user
        for (k,v) in webresp.headers.items():
            cherrypy.response.headers[k]=v
        cherrypy.response.status = webresp.code
        return (webresp.body or "")

    
    def handleCheckIDRequest(self, oidrequest):
        """
        This is where we should check the authenticity of the user and if the
        consumer site (the remote site requesting user information and
        authentication) is trustfull.

        The claimed id is the one that comes with the oidrequest. If
        no id came in the request, it means we have to ask one to the user.
        The id is authentic if it matches the DN of the certificate being
        used. If there is no certificate, then it must match a password.

        After authenticating the id, this method checks if the consumer
        is allowed to get user information. It does that by querying the
        registration service.
        """

        # First check if there is a user certificate
        #userDN = cherrypy.request.headers.get('Cms-Client-S-Dn', None)
        #access = cherrypy.request.headers.get('Cms-Auth-Status', None)
        userDN = cherrypy.request.headers.get('Ssl-Client-S-Dn', None)
        access = cherrypy.request.headers.get('Ssl-Client-Verify', None)
        if userDN != '(null)' and access == 'SUCCESS':
            # Means that the user certificate was authenticated by the frontend
            userfromdn = self.userstore.getuserbydn(userDN)
            if userfromdn:
               ## Ignores what was setup before as the identifier for this user
               #cherrypy.request.params['identifier'] = user
               sessuser=get_username()
               if sessuser and sessuser != userfromdn:
                   # First, will logout the user (thus, killing the session)
                   set_username(None) 
                   # Then, redirect it back to generate another session
                   # Can not use encodeToURL() because it doesn't put the
                   # sreg data request
                   #raise HTTPRedirect(oidrequest.encodeToURL(self.base_path+'openidserver'))
                   # **TO FIX** : the following internal redirect does not accept full URLs.
                   raise cherrypy.InternalRedirect(self.base_path+'openidserver'+'?'+urllib.urlencode(cherrypy.request.params))
                   
               set_username(userfromdn) # Does the user "login"!

        # Checks if this session is already authenticated
        sessuser = get_username()
        if not sessuser:
            # User did not authenticate yet 
            # So, try an user/pass authentication
            return self.webpages.showLoginPage(self.base_path,
                   success_to=self.base_path+'openidserver'+'?'
                            + urllib.urlencode(cherrypy.request.params),
                   fail_to=oidrequest.getCancelURL())
                                                    
        # Now should check the TRUST (the external site). The identity must had
        # been setup before as a query argument. So it ignores the identity
        # that came in the original oidrequest. The consumer site should
        # not choose the user (as agreed with Simon).
        myid = self.base_path + 'id/' + sessuser
        if self.truststore.allow(oidrequest.trust_root):
            oidresponse = oidrequest.answer(True, identity=myid)
            self.addSRegResponse(oidrequest, oidresponse, sessuser)
        else:
            oidresponse = oidrequest.answer(False)
        
        return self.displayOidResponse(oidresponse)

    def checkAuth(self, user, password):
        """Check that the request contains either a valid username:password"""
        return self.userstore.checkpass(user, password)

    def addSRegResponse(self, oidrequest, oidresponse, username):
        """
        The openid sreg extension is used to pass additional information
        about the authenticated user. In the CMS openid service, we use it to
        for sending authorization information: roles (or 'permissions'),
        fullname and DN of the user.
        """
        sreg_req = sreg.SRegRequest.fromOpenIDRequest(oidrequest)
        user = self.userstore.get(username)
        # Have to turn the users permission dict into json, needs to be a string
        user['permissions'] = self.encoder.encode(user['permissions'])
        sreg_data = user
        sreg_resp = sreg.SRegResponse.extractResponse(sreg_req, sreg_data)
        oidresponse.addExtension(sreg_resp)

    @cherrypy.expose
    def yadis(self,*args,**kwargs):
        """
        Yadis is a protocol for id discovery. The consumer (OidApp) uses it
        to find one or more OpenID providers (OidServers) able to authenticate
        the user. Since we will not allow users to use their Google, Yahoo, etc
        openids, there would be no need for it.

        However, we will not touch it just yet to avoid other compatibility
        problems that would arise. For instance, if the underlying openid
        library used by the OidApp issues a discovery request and does not
        provide an option to disable it.
        """
        username = cherrypy.request.path_info.split('/')[-1]
        self.info("YADIS USER IS: %s" % username)
        return self.webpages.showYadis(self.base_path, username)

    @cherrypy.expose
    def serveryadis(self):
        self.info("SHOW SERVER YADIS")
        return self.webpages.showServerYadis(self.base_path)

    @cherrypy.expose
    def id(self, *args, **kwargs):
        """Shows information about a specific openid user URL"""
        username = cherrypy.request.path_info.split('/')[-1]
        userinfo = self.userstore.get(username)
        return self.webpages.showIdPage(self.base_path,
                                        cherrypy.request.path_info,
                                        userinfo)

    @cherrypy.expose
    def default(self, *args, **kwargs):
        """Called when the server doesn't know how to handle the request"""
        raise cherrypy.HTTPError(404, 'Invalid page.')

#-------------------------------------------------------------------------------

class OidServerWebPages:
    def showMainPage(self, base_path):
        yadis_tag = '<meta http-equiv="x-xrds-location" content="%s">'%\
            (base_path + 'serveryadis')
        user = get_username()
        if user:
            openid_url = base_path + 'id/' + user
            user_message = """\
            <p>You are logged in as %s. Your OpenID identity URL is
            <tt><a href=%s>%s</a></tt>.</p>
            """ % (user, quoteattr(openid_url), openid_url)
        else:
            user_message = """\
            <p>You are not <a href='%slogin'>logged in</a>.</p>""" % base_path

        return self.showPage(base_path, 200, 'Main Page',
                             head_extras = yadis_tag, msg='''\
        <p>This is an CMS OpenID server.</p>

        %s

        <p>The URL for this server is <a href=%s><tt>%s</tt></a>.</p>
        ''' % (user_message, quoteattr(base_path), base_path))


    def showAboutPage(self, base_path):
        endpoint_url = base_path + 'openidserver'

        def link(url):
            url_attr = quoteattr(url)
            url_text = cgi.escape(url)
            return '<a href=%s><code>%s</code></a>' % (url_attr, url_text)

        def term(url, text):
            return '<dt>%s</dt><dd>%s</dd>' % (link(url), text)

        resources = [
            (base_path, "CMS OpenID Server"),
            ('http://www.openidenabled.com/',
             'An OpenID community Web site'),
            ('http://www.openid.net/', 'the official OpenID Web site'),
            ]

        resource_markup = ''.join([term(url, text) for url, text in resources])

        return self.showPage(base_path, 200, 'This is an OpenID server',
                             msg="""\
        <p>%s is an OpenID server endpoint.<p>
        <p>For more information about OpenID, see:</p>
        <dl>
        %s
        </dl>
        """ % (link(endpoint_url), resource_markup,))

    # **TO FIX** :
    #    global name base_path is not defined
    def showErrorPage(self, error_message):
        return self.showPage(base_path, 400, 'Error Processing Request',
                             err='''\
        <p>%s</p>
        <!--

        This is a large comment.  It exists to make this page larger.
        That is unfortunately necessary because of the "smart"
        handling of pages returned with an error code in IE.

        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************

        -->
        ''' % error_message)

    def showIdPage(self, base_path, path, userinfo):
        link_tag = '<link rel="openid.server" href="%sopenidserver">' %\
                   base_path
        yadis_loc_tag = '<meta http-equiv="x-xrds-location" content="%s">' %\
            (base_path+'yadis/'+path[4:])
        disco_tags = link_tag + yadis_loc_tag
        ident = base_path + path[1:]

        msg =  '<p>User information:</p>\n'
        msg += '<table border="0">\n'
        for k in userinfo.keys():
            msg += '<tr><td><b>%s</b></td><td>%s</td></tr>\n' % \
                   (k, userinfo[k])
        msg += '</table>\n'

        return self.showPage(base_path, 200, 'Identity Page',
                             head_extras=disco_tags, msg='''\
        <p>This is an identity page for <b>%s</b>.</p>
        %s
        ''' % (ident, msg))

    def showYadis(self, base_path, username):
        endpoint_url = base_path + 'openidserver'
        identity = base_path + 'id/' + username
        webpage = """\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type>%s</Type>
      <Type>%s</Type>
      <URI>%s</URI>
      <LocalID>%s</LocalID>
    </Service>

  </XRD>
</xrds:XRDS>
"""%(discover.OPENID_2_0_TYPE, discover.OPENID_1_0_TYPE,
     endpoint_url, identity)

        # Now it sends the web response to the user
        cherrypy.response.status = 200
        cherrypy.response.headers['Content-type'] = 'application/xrds+xml'
        return webpage

    def showServerYadis(self, base_path):
        endpoint_url = base_path + 'openidserver'
        webpage = """\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type>%s</Type>
      <URI>%s</URI>
    </Service>

  </XRD>
</xrds:XRDS>
"""%(discover.OPENID_IDP_2_0_TYPE, endpoint_url,)

        # Now it sends the web response to the user
        cherrypy.response.status = 200
        cherrypy.response.headers['Content-type'] = 'application/xrds+xml'
        return webpage

    def showLoginPage(self, base_path, success_to, fail_to):
        return self.showPage(base_path, 200, 'Login Page',
                             form='''\
        <h2>Login</h2>
        <p>The identifier is your CERN afs login name.</p>
        <form method="GET" action="%sloginsubmit">
          <input type="hidden" name="success_to" value="%s" />
          <input type="hidden" name="fail_to" value="%s" />
          <input type="text" name="identifier" value="" />
          <input type="password" name="password" value="" />
          <input type="submit" name="submit" value="login" />
          <input type="submit" name="submit" value="cancel" />
        </form>
        ''' % (base_path, success_to, fail_to))

    def showPage(self, base_path, response_code, title,
                 head_extras='', msg=None, err=None, form=None):
        username = get_username()
        if username is None:
            user_link = '<a href="%slogin">not logged in</a>.' % base_path
        else:
            fdata = {'base_path': base_path,
                     'user': username,}
            # The logout is a login submission with no user name (user=None)
            user_link = 'logged in as <a href="%(base_path)sid/%(user)s">%(user)s</a>.<br /><a href="%(base_path)sloginsubmit?submit=login&success_to=%(base_path)slogin">Log out</a>' % \
                        fdata 

        body = ''

        if err is not None:
            body +=  '''\
            <div class="error">
              %s
            </div>
            ''' % err

        if msg is not None:
            body += '''\
            <div class="message">
              %s
            </div>
            ''' % msg

        if form is not None:
            body += '''\
            <div class="form">
              %s
            </div>
            ''' % form

        contents = {
            'title': 'CMS OpenID Server - ' + title,
            'head_extras': head_extras,
            'body': body,
            'user_link': user_link,
            'base_path': base_path,
            }

        webpage = '''<html>
  <head>
    <title>%(title)s</title>
    %(head_extras)s
  </head>
  <style type="text/css">
      h1 a:link {
          color: black;
          text-decoration: none;
      }
      h1 a:visited {
          color: black;
          text-decoration: none;
      }
      h1 a:hover {
          text-decoration: underline;
      }
      body {
        font-family: verdana,sans-serif;
        width: 50em;
        margin: 1em;
      }
      div {
        padding: .5em;
      }
      table {
        margin: none;
        padding: none;
      }
      .banner {
        padding: none 1em 1em 1em;
        width: 100%%;
      }
      .leftbanner {
        text-align: left;
      }
      .rightbanner {
        text-align: right;
        font-size: smaller;
      }
      .error {
        border: 1px solid #ff0000;
        background: #ffaaaa;
        margin: .5em;
      }
      .message {
        border: 1px solid #2233ff;
        background: #eeeeff;
        margin: .5em;
      }
      .form {
        border: 1px solid #777777;
        background: #ddddcc;
        margin: .5em;
        margin-top: 1em;
        padding-bottom: 0em;
      }
      dd {
        margin-bottom: 0.5em;
      }
  </style>
  <body>
    <table class="banner">
      <tr>
        <td class="leftbanner">
          <h1><a href="%(base_path)s">CMS OpenID Server</a></h1>
        </td>
        <td class="rightbanner">
          You are %(user_link)s
        </td>
      </tr>
    </table>
%(body)s
  </body>
</html>
''' % contents

        # Now it sends the web response to the user
        cherrypy.response.status = response_code
        cherrypy.response.headers['Content-type'] = 'text/html'
        return webpage

#-------------------------------------------------------------------------------

def get_username():
    """
    Gets the username from the cherrypy session. The username will only
    be available after the user authenticated successfully. If not
    authenticated, it will return None.
    """
    oidsession = get_session()
    return oidsession['username']

def set_username(username):
    oidsession = get_session()
    if username:
        oidsession['username'] = username
    else:
        cherrypy.lib.sessions.expire() # Does a logout by expiring the session
    
def get_session():
    """
    Uses cherrypy sessions instead of implementing by my own because:
    - The sessionid is bounded to the user-agent and then less subject
    to sessionid hijacking (when the cookie is theft or the sessionid
    is guessed)
    - It has a protection against session fixation attacks
    (see http://en.wikipedia.org/wiki/Session_fixation)
    - It allows me to choose the backend to store session information
    
    Another more secure solution to consider would be to use the SSL/TLS
    session identifier. But it would require changing the frontend config
    to set the SSL_SESSION_ID variable into the request sent to the backend
    """
    oidsession = cherrypy.session.get(SESSION_NAME, None)
    if not oidsession:
        cherrypy.session[SESSION_NAME] = {}
        cherrypy.session[SESSION_NAME]['username'] = None

    return cherrypy.session[SESSION_NAME]
    
def quoteattr(nonhtmltext):
    'Prepares a text string to be used with HTML'
    htmltext = cgi.escape(nonhtmltext, 1)
    return '"%s"' % (htmltext,)
