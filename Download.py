Install Brew
------------
https://osxdaily.com/2018/03/07/how-install-homebrew-mac-os/
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


Adding SSH
-----------
ssh-keygen -t rsa -C "nikitha.r@pwc.com"
cat < ~/.ssh/id_rsa.pub
  -> Copy the entire thing to add new ssh or public key(title can be given anything)
git clone git@ssh.dev...


Download Git
---------------
https://sourceforge.net/projects/git-osx-installer/

  
Download Docker
---------------
https://hub.docker.com/editions/community/docker-ce-desktop-mac/
  -> The Stable version is fully baked and tested, and comes with the latest GA release of Docker.	
  
Download Pip3
---------------
brew install python will install pip3

Download pip
---------------
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo easy_install pip


Download Virtualenv
------------------------------
pip install virtualenv
