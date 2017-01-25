#EggZlist

Built using the Flask micro-framework for Python.

##Installation

1) Clone into a directory

2) Change into new EggZlist directory

3) Create a virtual environment and activate it

    virtualenv flask
    source flask/bin/activate

4) Install requirements

    pip install -r requirements.txt

5) Create the database for the market side

    ./db_create.py

6) Run the server

    sudo ./run.py

###**BOOM** just like that, you're done.

## Remember to delete any directories in static/uploads when refreshing the DB


#Instructions for using Gulp and Sass with Nodejs

1) Install Nodejs (This installs Nodejs version 7, but other versions should work too)

    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
    sudo apt-get install -y nodejs

2) Install Gulp globally

    sudo npm install gulp -g

(This assumes a package.json file, gulpfile.js, and node_modules folder exists!)
3) To process SCSS files and use other Gulp utiltilies designated in gulpfile.js use

    gulp
