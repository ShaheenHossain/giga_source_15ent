[![Build Status](http://runbot.gigasource.de/runbot/badge/flat/7/master.svg)](http://runbot.gigasource.de/runbot/repo/git-github-com-giga-enterprise-7)
[![Tech Doc](http://img.shields.io/badge/14.0-docs-875A7B.svg?style=flat)](http://www.gigasource.de/documentation/15.0)
[![Help](http://img.shields.io/badge/master-help-875A7B.svg?style=flat)](https://www.gigasource.de/forum/help-1)
[![Nightly Builds](http://img.shields.io/badge/master-nightly-875A7B.svg?style=flat)](http://nightly.gigasource.de/)

Giga
----

Giga is a suite of web based open source business apps.

The main GigaSource Apps include an <a href="https://www.gigasource.de/app/crm">Open Source CRM</a>,
<a href="https://www.gigasource.de/app/website">Website Builder</a>,
<a href="https://www.gigasource.de/app/ecommerce">eCommerce</a>,
<a href="https://www.gigasource.de/app/inventory">Warehouse Management</a>,
<a href="https://www.gigasource.de/app/project">Project Management</a>,
<a href="https://www.gigasource.de/app/accounting">Billing &amp; Accounting</a>,
<a href="https://www.gigasource.de/app/point-of-sale-shop">Point of Sale</a>,
<a href="https://www.gigasource.de/app/employees">Human Resources</a>,
<a href="https://www.gigasource.de/app/lead-automation">Marketing</a>,
<a href="https://www.gigasource.de/app/manufacturing">Manufacturing</a>,
<a href="https://www.gigasource.de/app/purchase">Purchase Management</a>,
<a href="https://www.gigasource.de/">...</a>

GigaSource Apps can be used as stand-alone applications, but they also integrate seamlessly so you get
a full-featured <a href="https://www.gigasource.de">Open Source ERP</a> when you install several Apps.

Getting started with Giga
-------------------------

For a standard installation please follow the <a href="https://www.gigasource.de/documentation/15.0/administration/install/install.html">Setup instructions</a>
from the documentation.

If you are a developer you may type the following command at your terminal:

    wget -O- https://raw.githubusercontent.com/giga/giga/master/setup/setup_dev.py | python

Then follow <a href="https://www.gigasource.de/documentation/15.0/developer/howtos.html">the developer tutorials</a>

For Giga employees
------------------

To add the giga-dev remote use this command:

    $ ./setup/setup_dev.py setup_git_dev

To fetch giga merge pull requests refs use this command:

    $ ./setup/setup_dev.py setup_git_review
