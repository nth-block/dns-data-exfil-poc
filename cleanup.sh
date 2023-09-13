# In case you are not comfortable with git reverts
rm victim/an-ip-file.txt victim/encoded victim/pass.tar.gz victim/xaa*
rm attacker/an-ip-file.txt attacker/reconstruction attacker/reconstructed.tar.gz

# In case you are a git client God...
git clean -f -d
