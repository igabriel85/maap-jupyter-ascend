This is a template of documentation. Please change each section by correct information
Headings

# This is an H1
## This is an H2
###### This is an H6

This is also an H1
==================

This is also an H2
------------------

Paragraphs

Paragraphs are separated by empty lines. To create a new paragraph, press <return> twice.

Paragraph 1

Paragraph 2

Character styles

*Italic characters* 
_Italic characters_
**bold characters**
__bold characters__
~~strikethrough text~~

Unordered list

*  Item 1
*  Item 2
*  Item 3
    *  Item 3a
    *  Item 3b
    *  Item 3c

Ordered list

1.  Step 1
2.  Step 2
3.  Step 3
    1.  Step 3.1
    2.  Step 3.2
    3.  Step 3.3

List in list

1.  Step 1
2.  Step 2
3.  Step 3
    *  Item 3a
	*  Item 3b
	*  Item 3c

Quotes or citations

Introducing my quote:

> Neque porro quisquam est qui 
> dolorem ipsum quia dolor sit amet, 
> consectetur, adipisci velit...

Inline code characters

Use the backtick to refer to a `function()`.
 
There is a literal ``backtick (`)`` here.

Code blocks

Indent every line of the block by at least 4 spaces.

This is a normal paragraph:

    This is a code block.
    With multiple lines.

Alternatively, you can use 3 backtick quote marks before and after the block, like this:

```
This is a code block
```

To add syntax highlighting to a code block, add the name of the language immediately
after the backticks: 

```javascript
var oldUnload = window.onbeforeunload;
window.onbeforeunload = function() {
    saveCoverage();
    if (oldUnload) {
        return oldUnload.apply(this, arguments);
    }
};
```

Links to external websites

This is [an example](http://www.example.com/) inline link.

[This link](http://example.com/ "Title") has a title attribute.

Links are also auto-detected in text: http://example.com/

Images

Inline image syntax looks like this:

![Alt text](/path/to/image.jpg)
![Alt text](/path/to/image.png "Optional title attribute")
![Alt text](/url/to/image.jpg)

For example:

...
![Mockup for feature A](http://monosnap.com/image/bOcxxxxLGF.png)
...

Reference image links look like this:

![Alt text][id]

where 'id' is the name of a previously defined image reference, using syntax similar to link references:

[id]: url/to/image.jpg "Optional title attribute"

For example:

...
<--Collected image definitions-->
[MockupA]: http://monosnap.com/image/bOcxxxxLGF.png "Screenshot of Feature A mockup" 
...
<!--Using an image reference-->
![Mockup for feature A][MockupA]
...

Tables

| Day     | Meal    | Price |
| --------|---------|-------|
| Monday  | pasta   | $6    |
| Tuesday | chicken | $8    |

Backslash escapes

Certain characters can be escaped with a preceding backslash to preserve the literal display of a character instead of its special Markdown meaning. This applies to the following characters:

\  backslash
`  backtick
*  asterisk
_  underscore
{} curly braces
[] square brackets
() parentheses
#  hash mark
>  greater than
+  plus sign
-  minus sign (hyphen)
.  dot
!  exclamation mark

