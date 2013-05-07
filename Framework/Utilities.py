def selectFromDict (argsDict, *keys):
    returnDict = {}
    for x in keys:
        returnDict[x] = argsDict [x]
    return returnDict
