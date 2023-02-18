# FLint
## Flexible Linter for most languages
### Make Html files from your Project's Documentation.

# Usage
- Clone this repository somewhere common
- Copy the .flint-ignore & flint.bat into your projects
- Change the settings in flint.bat
- Add or remove file/directory paths in .flint-ignore
- Document your code and run flint.bat

## Document with Doc-Blocks
### C, C++, C#, Java, Rust
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
- ex. //>> BlockName .view .container .etc 
- Copy the sample styles.css next to docs.html
- Sample includes styling for react-native projects
