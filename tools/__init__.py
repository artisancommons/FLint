
from os import listdir
from os.path import isdir as path_isdir
from os.path import exists as dir_exists
from os import mkdir

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
                resultGroups[blockName].append(f'<p class="box default-block">\n' + result + "</p>\n")
            
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
            # escape html 'tags'
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
                currentLintResult[group].insert(0, '<div class="box group-blob">\n')
            else:  # group found, use inner div
                currentLintResult[group].insert(0, '<div class="box group-blob-inner">\n')
            
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


def make_html(subDir, content):
    return f'<!DOCTYPE html>\n<html>\n<head>\n<link rel="stylesheet" href="{"../" if subDir else ""}styles.css">\n</head>\n<body>\n{content}\n</body>\n</html>\n'

def make_pretty(subDir, content):
    newContent = ""

    # local function for tab spacing
    def make_tabs(count):
        tabs = list_to_string(['    ' for e in range(count)])
        return tabs

    def make_home_link():
        return make_link("./index", subDir) + '\n'

    contentLines = content.split('\n')
    contentLines.insert(0, make_home_link())

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
    return make_html(subDir, f'\n<div class="project-result-body">\n\n{newContent}\n</div>\n')

def write_file(subDir, outputPath, data, linkpaths):
    print(f"using {linkpaths}")
    with open(outputPath, 'w') as fd:

        # handle merge flag
        if type(data) is dict:
            # start with previous page link
            dump = f"{linkpaths[0]}"
            
            # tally contents into single string
            for key in data:
                dump += list_to_string(data[key])
            
            # end with next page link
            dump += linkpaths[1]
            
            # format all parsed content
            dump = make_pretty(subDir, dump)
            fd.write(dump)
        else:
            # write single file of all content
            content = list_to_string(data)
            
            # wrap (previous page) file_content (next page) 
            content = f"\n{linkpaths[0]}\n{content}\n{linkpaths[1]}\n"
            fd.write(make_pretty(subDir, content))


# return path excluding last two segments  
def fix_path(path):
    newPath = ""
    # split path by /
    pathSplit = path.split('/')
    for i in pathSplit[:-1]:
        newPath += i + '/'
    return newPath[:-1]

# try make dir
def force_make_dir(path):
    if not dir_exists(path):
        mkdir(path)

# make href link
def make_link(data, back=False):
    # calculate depth
    r = len(data.split('/'))
    
    if not back:  # index.html
        r - 3
        dots = './'
        ref = "page-link"
    else:         # root or nested pages
        dots = f"{list_to_string(['.' for i in range(0, r if r >= 0 else 0)])}/{'' if back else ''}"
        ref = "page-sub-link"

    beg = f'<a class="{ref}" href="{dots}{data}.html" >'
    
    segs = data.split("/")[1:]
    string = list_to_string([s + " " for s in segs])
    
    end = f'<h4 class="link-title">{string}</h4></a>\n'
    
    return beg + end 

# make header of n size
def make_title(group, n=6):
    headerStyles = {
        6: "tiny",
        5: "small",
        4: "normal",
        3: "medium",
        2: "large",
        1: "max",
    }
    return f'<h{n} class="header-base header-{headerStyles[n]}">{group}</h{n}>\n'

def make_index(outputPath, groups):
    # index page content
    inner = ""
    
    # map for header sizes (h1, h2, etc.)
    scalars = {}
    rootGroup = ""
    for key in groups:
        # split group name, use first path
        rootGroup = key.split('/')[0]
        
        # initial header size
        if rootGroup not in scalars:
            scalars[rootGroup] = 1
            continue

        # increase header size
        scalars[rootGroup] += 1

    # min/max for header (1-6)
    def min_header_size(a, b):
        return a if a <= b else b
    def max_header_size(a, b):
        return b if b >= a else a

    def make_list_begin():
        return '<ul>\n'
    def make_list_item(item):
        return f'<li>{item}</li>\n'
    def make_list_end():
        return '</ul>\n'

    # track unique titles
    titlesMade = []
    first = True
    for key in groups:
        skey = key.split('/')[0]
        # make unqiue title
        if fix_path(key) not in titlesMade:
            inner += make_title(fix_path(key), (max_header_size(7 - min_header_size(scalars[skey], 3), 1)))
            titlesMade.append(fix_path(key))
            
            if first == False:
                inner += make_list_end()
            inner += make_list_begin()
            first = False
            
        
        # concatenate link tag
        inner += make_list_item(make_link(key))
    inner += make_list_end()
    inner += '<br>\n'
    
    # wrap content into html format
    indexFile = inner
    # write the index.html file
    with open(f"{outputPath}/index.html", 'w') as fd:
        fd.writelines(make_pretty(False, indexFile))


def make_links_list(groups):
    # turn dict_keys into list
    rkeys = [key for key in groups]
    
    # set wrap bounds
    mod = len(rkeys)-1
    
    # link set cache
    linkset = ['', '']
    
    # href link nodes (previous page -> next page)
    # based on group names
    linksets = {}
    
    for i in range(0, len(rkeys)):
        # handle index wrapping
        f1 = ((i + 1) % mod)
        f2 = ((i + 2) % mod)

        # assign links
        linkset[0] = make_link(rkeys[f1], True)
        linkset[1] = make_link(rkeys[f2], True)

        # copy set into group map
        linksets[rkeys[i]] = linkset.copy()

    return linksets


# main entry
def do_lint(lintType, ioArgs, lintIgnore):
    # create linter instance and run lint method
    linter = Linter(ioArgs, lintIgnore)
    result = linter.lint(lintType)
    
    outputPath = ioArgs[1]
    
    groups = result.keys()
    
    # create index.html from groups
    make_index(outputPath, groups)

    doesMerge = lintType == LINT_TYPE_MDIR
    # dump parsed contents into a single file 
    if doesMerge:
        force_make_dir(fix_path(outputPath))
        write_file(False, f'{outputPath}.html', result, ["<br>", "<br>"])

    # dump parsed contents into files specified by block names
    else:
        linksets = make_links_list(groups)

        for group in result:
            linkset = linksets[group]
            force_make_dir(fix_path(f'{outputPath}/{group}'))
            write_file(True if len(outputPath.split('/')) > 2 else False, f'{outputPath}/{group}.html', result[group], linkset)
