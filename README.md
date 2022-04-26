yum -y install https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome-stable-99.0.4844.17-1.x86_64.rpm
wget https://chromedriver.storage.googleapis.com/99.0.4844.17/chromedriver_linux64.zip
https://chromedriver.storage.googleapis.com/index.html

##查询版本
https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable





yum install -y mysql-devel
pip3 install setuptools-rust

pip3 install wheel

pip3 install cryptography --only-binary=:all:

yum install -y python3-devel



crontab:
0 8 * * * cd /home/fs; /usr/bin/python3 /home/fs/start.py