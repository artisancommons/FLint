
from os import listdir
from os.path import isdir as path_isdir

from .util import (
    list_to_string,
    read_file,
)


# marker tokens #
TOKEN_HASH         = "#>>"
TOKEN_DOUBLE_SLASH = "//>>"
TOKEN_MULTI_START  = "/*>>"
TOKEN_MULTI_STOP   = "<<*/"

A_LEFT_ANGLE = '&#60'
A_RIGHT_ANGLE = '&#62'
# ------------- #

# lint types #
LINT_TYPE_FILE, LINT_TYPE_DIR, LINT_TYPE_MDIR = \
    "file",          "dir",         "mdir"
def evaluate_lint_type(args):
    if '-d' in args:
        return LINT_TYPE_DIR
    if '-md' in args:
        return LINT_TYPE_MDIR
    return LINT_TYPE_FILE

# ---------- #



# lint methods #
def is_token(line):
    return TOKEN_HASH         in line \
        or TOKEN_DOUBLE_SLASH in line \
        or TOKEN_MULTI_START  in line \
        or TOKEN_MULTI_STOP   in line

def parse_content(content):
    resultGroups = {}
    result = ""

    blockStyle = ""
    blockName = "base"
    inBlock = False
    
    for line in content:
        # clean line of spaces and new line characters
        strippedLine = line.lstrip().rstrip().strip('\n')
        # evaluate line for token (//>>, #>>)
        currentLineIsToken = is_token(strippedLine)

        # closing token is found
        if inBlock and currentLineIsToken:
            # reset parsing
            inBlock = False
            
            # no custom style found, using default
            if blockStyle == "":
                resultGroups[blockName].append(f'<p class="default-block">\n' + result + "</p>\n")
            
            else:  # if the block had (a) custom style(s)
                # account for 1 or more styles
                stylesList = blockStyle.split(' ')

                # style string, class="style1 style2"
                styles = ""
                for style in stylesList:
                    styles += f"{style[1:]} "
                
                # add block data with custom style(s)
                resultGroups[blockName].append(f'<p class="{styles[:-1]}">\n' + result + "</p>\n")
                blockStyle = "" # reset styles
            
            # reset result accumulator
            result = ""
            continue  # skip to next line

        elif currentLineIsToken:
            # token was found on the current line
            inBlock = True

            # grab the block name, may include style(s)
            blockName = strippedLine.split(' ')[1:]

            # does include custom style(s)
            if len(blockName) > 1:
                # cache each style into blockStyle
                for style in blockName[1:]:
                    blockStyle += f"{style} "
                blockStyle = blockStyle[:-1]
            
            # styles found or not, get the block name
            blockName = blockName[0]

            # handle invalid block name
            if len(blockName) <= 2:
                blockName = 'base'

            # cache the new block
            if blockName not in resultGroups:
                resultGroups[blockName] = []
            continue  # skip to next line

        # doc block accumulation
        if inBlock:
            result += line.replace('<', A_LEFT_ANGLE).replace('>', A_RIGHT_ANGLE)
    
    # groups of result data, based on blockName
    return resultGroups

# read and parse a single file, into a block map
def lint_file(filePath):
    print(f" -- processing file {filePath}")
    content = read_file(filePath)
    result = parse_content(content)
    return result


def is_ignored_path(targetRoot, dirPath, lintIgnore):
    projectDirFound = False
    targetPath = ""
    
    # finds project directory, then adds each following path
    for pathSegment in dirPath.split('/'):
        if pathSegment == targetRoot:
            projectDirFound = True
        if projectDirFound:
            targetPath += f"{pathSegment}/"
    
    # strip last /
    targetPath = targetPath[:-1]
    
    return [targetPath, targetPath in lintIgnore]
    

def ignore_current_path(currentLocalPath, lintIgnore):
    if currentLocalPath in lintIgnore:
        return True
    
    pathSplit = currentLocalPath.split('/')[-1:]
    
    line = ""
    # build path from last segments
    for segment in pathSplit:
        line += f"{segment}/"
    line = line[:-1]  # strip last /
    
    return line in lintIgnore
    

# recurrsively lint directories
def lint_dir(targetRoot, lintIgnore, dirPath):
    print(f"-\n processing directory {dirPath}")
    
    # early return for ignored path
    isIgnoredPathResult = is_ignored_path(targetRoot, dirPath, lintIgnore)
    if isIgnoredPathResult[1]:
        return {}

    projectLocalPath = isIgnoredPathResult[0]

    currentDirPaths = listdir(dirPath)

    resultGroups = {}
    for path in currentDirPaths:
        currentAbsPath = f'{dirPath}/{path}'

        # check ignore map again
        currentLocalPath = f"{projectLocalPath}/{path}"
        if ignore_current_path(currentLocalPath, lintIgnore):
            continue
        
        currentLintResult = {}

        # branch to file or do recurrsive step in
        if path_isdir(currentAbsPath):
            currentLintResult = lint_dir(targetRoot, lintIgnore, currentAbsPath)
            if currentLintResult == {}:
                continue
        else:
            currentLintResult = lint_file(currentAbsPath)
            if currentLintResult == {}:
                continue

        # find group names that have been added already
        groupsAlreadyFound = []
        for group in currentLintResult:
            if group in resultGroups:
                groupsAlreadyFound.append(group)

        # each group name
        for group in currentLintResult:
            # if empty group
            if len(currentLintResult[group]) == 0:
                continue

            # new group
            if group not in groupsAlreadyFound:
                currentLintResult[group].insert(0, '<div class="group-blob">\n')
            else:  # group found, use inner div
                currentLintResult[group].insert(0, '<div class="group-blob-inner">\n')
            
            # add or assign group's list data
            if group in resultGroups:
                resultGroups[group].append(currentLintResult[group])
            else:
                resultGroups[group] = currentLintResult[group]
            
            # close div tag
            resultGroups[group].append("</div>\n")
    
    print('-')
    print('')  # console output spacing
    return resultGroups
# ------------ #

# @ioPaths: input and output paths
# @lintIgnore: path ignore map
class Linter():
    def __init__(self, ioPaths, lintIgnore):
        self.ioPaths = ioPaths
        self.lintIgnore = lintIgnore
        
    def lint(self, lintType):
        inputPath, outputPath = self.ioPaths[0], self.ioPaths[1]

        # recurrsively parse file content into data map
        result = {}
        if lintType == LINT_TYPE_FILE:
            result = lint_file(inputPath)
        else:
            result = lint_dir(inputPath.split('/')[-1], self.lintIgnore, inputPath)

        projectName = outputPath.split('/')[-1]

        return result


def make_pretty(content):
    newContent = ""

    # local function for tab spacing
    def make_tabs(count):
        tabs = list_to_string(['    ' for e in range(count)])
        return tabs

    contentLines = content.split('\n')

    stepsIn, stepsOut = 1, 0
    closerFound = False
    for line in contentLines:
        if len(line) == 0:
            continue
        # closing tag found, step out
        if line[0:2] == "</":
            stepsOut += 1
            closerFound = True

        # opening tag found, step in
        elif line[0] == "<":
            stepsIn += 1
            closerFound = False

        # escapes everything
        #line = line.replace('<', A_LEFT_ANGLE).replace('>', A_RIGHT_ANGLE)
       
        if closerFound:  # closing tag spacing
            newContent += f"{make_tabs(stepsIn - stepsOut)}{line}\n"
        elif line[0] != '<':  # content line
            newContent += f"{make_tabs(stepsIn - stepsOut)}{line}\n"
        else:  # opening tag spacing
            newContent += f"{make_tabs((stepsIn - stepsOut) - 1)}{line}\n"

    # return wrapped formatted data
    return f'\n<div class="project-result-body">\n\n{newContent}\n</div>\n'

def write_file(outputPath, data):
    with open(outputPath, 'w') as fd:
        # handle merge flag
        if type(data) is dict:
            dump = ""
            # tally contents into single string
            for key in data:
                dump += list_to_string(data[key])
            # format all parsed content
            dump = make_pretty(dump)
            fd.write(dump)
        else:
            # write single file of all content
            fd.write(make_pretty(list_to_string(data)))

# main entry
def do_lint(lintType, ioArgs, lintIgnore):
    # create linter instance and run lint method
    linter = Linter(ioArgs, lintIgnore)
    result = linter.lint(lintType)

    outputPath = ioArgs[1]

    doesMerge = lintType == LINT_TYPE_MDIR
    # dump parsed contents into a single file 
    if doesMerge:
        write_file(f'{outputPath}.html', result)

    # dump parsed contents into files specified by block names
    else:
        for group in result:
            write_file(f'{outputPath}/{group}.html', result[group])
