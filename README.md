# FLint
## Flexible Linter for most languages
### Make Html files from your Project's Documentation.

# Usage
#### Steps
- Clone this repository somewhere common
- Copy the .flint-ignore & flint.bat into your projects
- Change the settings in flint.bat
- Add or remove file/directory paths in .flint-ignore
- Document your code and run flint.bat
- Please read instructions in flint.bat
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

## Document with Doc-Blocks
### C, C++, C#, Java, Rust, PHP
- Start and Close a Doc-Block   with //>>
- Start a Doc-Block(multi-line) with /*>>
- Close a Doc-Block(multi-line) with <<*/
### Python
- Start and Close a Doc-Block with #>>
### Non-Programming
- Can also be used for plain text files.
#### Custom Styling
- Following a Doc-Block Start:
-  Add 'space-separated' styles
- Example. //>> BlockName .view .container .etc 
- Copy the sample styles.css next to docs.html
- Sample includes styling for react-native projects
