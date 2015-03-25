# IN PROGRESS #

# Introduction #

RegiMUN is a [Django framework](http://www.djangoproject.com) application.  Your web server should have Django installed before installing RegiMUN.  See the Django website for instructions on installing the framework, or your web hosting provider may have a one-click install through your site's control panel.

Installing RegiMUN requires command-line access to your web server (typically via SSH), but does not require administrator access.  The following instructions assume that you are using the command line on your server.

# Download RegiMUN #

To download the RegiMUN code, run:
```
svn checkout http://regimun.googlecode.com/svn/trunk/ regimun-read-only
```

# Install Python Libraries #

RegiMUN depends on Python libraries that do not typically come installed on a web server.
  * [Report Lab Toolkit](http://pypi.python.org/pypi/reportlab)
  * [HTML5Lib](http://pypi.python.org/pypi/html5lib/0.90)
  * [Pisa](http://pypi.python.org/pypi/pisa)
  * [Recaptcha Client](http://pypi.python.org/pypi/recaptcha-client)

### With Server Admin Access and easy\_install ###

Run the following command:
```
easy_install reportlab html5lib pisa recaptcha-client
```

### Without Server Admin Access ###

Download the packages from the above sites on your server, and install them to a non-admin directory. Add the install paths to the PYTHON\_PATH environment variable.

# Details #

Add your content here.  Format your content with:
  * Text in **bold** or _italic_
  * Headings, paragraphs, and lists
  * Automatic links to other wiki pages