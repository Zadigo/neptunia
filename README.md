# Neptunia

Neptunia is a simple web crawler created specifically for web marketing. It includes automation modules and middlewares for SEO auditing, email and telephone scrapping.

## How to use


## Middlewares

Neptunia comes with a set of base middlewares which are executed after a request has been sent.

### TextMiddleware

This middleware analysis the text of the current page. It analysis the total amount of words and .


### EmailMiddleware

This middleware collects emails on the current page.


### ImageMiddleware

This middleware collects images of different kinds.


### SEOMiddleware

This middleware runs a simple SEO audit on the page by identifying a few elements:

* The title length
* The description length
* The most common words
* The page status code
