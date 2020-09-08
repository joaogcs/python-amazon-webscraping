Requirements

  pip install selenium

Overview

This is a tool to automate a search in https://amazon.com.br.
You can search for any text and retrieve the result to a csv in the order they were listed.
The properties you'll get are:
    Page_Found: the result page number which the item was found
    Product name: the exact name showed in result page
    Price: the exact price in BRL, it can be None as the page shows some items without price

More items properties can be easily added, such as url, image_link and many others..
