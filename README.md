# FLint
## Flexible Linter for most languages
### Make Html files from your Project's Documentation.

# Usage
#### Steps
- Clone this repository somewhere common ```ex. user/my-tools```
- Copy the ```.flint-ignore``` & ```flint.bat``` into your projects
- Change the settings in ```flint.bat```
- Add or remove file/directory paths in ```.flint-ignore```
- Document your code and run ```flint.bat```
- Please read instructions in ```flint.bat```
#### Examples
```code
//>> Page/SubPage
// this is captured
//>>
```
```code
/*>> Page/SubPage
this is captured
<<*/
```
```code
#>> Page/SubPage
# this is captured
#>>
```

## Document with Doc-Blocks
### C, C++, C#, Java, Rust, PHP
- Start and Close a Doc-Block   with //>>
```code
//>> MyDocBlock
// this is captured
//>>
```
- Start a Doc-Block(multi-line) with /*>>
- Close a Doc-Block(multi-line) with <<*/
```code
/*>> MyDocBlock
this is captured
<<*/
```

### Python
- Start and Close a Doc-Block with #>>
```code
#>> MyDocBlock
# this is captured
#>>
```

### Non-Programming
- Can also be used for plain text files.
- Either notation can be used
```code
//>> MyDocBlock
this is captured
//>>

/*>> MyDocBlock
this is captured
<<*/

#>> MyDocBlock
this is captured
#>>
```

#### Custom Styling
- Copy the sample styles.css next to docs.html
- Sample includes styling for react-native projects
- 
- After Starting a Doc-Block:
  - Add 'space-separated' styles
  - ex.  ```//>> MyDocBlock .my-custom-class```
##### Text File Style Examples.
```code 
// multiple styles can be used
//>> MyBlockName .view .container .classes-etc 
```
```code
! Note: this notation style only works in non-code files !

//>> Component/ListView .box-component
 info about 'ListView' component
 uses 'box-component' class
//>>

/*>> Screens/Main .box-main
 info about 'Main' Screen
 uses 'box-main' class
<<*/

#>> Routes/Api .box-endpoints
 info about api routes
 uses 'box-endpoints' class
#>>
```
