# Coronavirus: A Concrete Poetry

You can view the work [on this webpage](http://jiwonshin.com/mol/week4/).

For the Concrete Poetry assignment, I wanted to use the Twitter API to gather tweets that include #coronavirus to rearrange the text in the shape of the virus particle.

I didn't get to implement the Twitter API because the developer keys that I applied for hasn't been approved yet, so instead, I collected top 8 tweets using the hashtag (last updated March 3, 9PM) manually. 

Each tweet is used to create an instance of WordVis class that creates divs and styles the shape in css. The rotation of each particle is done using css animation and the movement of each particle is done using setInterval function.

I couldn't figure out why some emojis show in the text while some don't in the visualized text. On the console window of the Chrome browser, the raw data of the texts show the emojis, but they don't show as divs in the html.

The full code of the work is available [here](index.html).
