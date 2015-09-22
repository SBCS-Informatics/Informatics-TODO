# SBCS-Informatics TODO

###Bash_extensions
- TODO: Fix Dir History
- Provides users with ZSH as default shell with helpful defaults & aliases
- Comes with access to commonly used general and biological software (typically the latest versions)

- How to use

```sh
# Source Bash Extensions file (Temporarily try it out)
source /data/SBCS-WurmLab/SBCS-Informatics/bash_extensions

# Backup existing .zshrc (This will be re-written otherwise).
mv ~/.zshrc ~/.zshrc.BAK

# Add ZSH and Extras to .bash_profile (This automatically uses the extensions each time you log in)
echo 'source /data/SBCS-WurmLab/SBCS-Informatics/bash_extensions' >> .bash_profile
```

###Linuxbrew
- brew install al bio-stuff

```sh
brew doctor
brew tap homebrew/science
brew install star htslib bamtools mafft bedops blast newick-utils emboss prank blat raxml bowtie2 genometools hmmer seqtk
```

- Other potential packages

```sh
curl wget ssh-copy-id awscli pandoc heroku-toolbelt htop links n pandoc-citeproc unison imagemagick parallel pv aircrack-ng ircii boot2docker lftp gcc cmake youtube-dl chktex latex2rtf lftp ncftp gd unrar tmux sshfs
```

### Set up multi-user Virtual env for Ruby, python, perl, R
- Is this already set up by ITS-research?
- Add documentation on how to use.

### Move /data/SBCS-Wurmlab/SBCS-Informatics to a more accessible location
- Currently can only be accessed by users in the  SBCS-WurmLab group
- i.e. something like /data/SBCS-Informatics or /data/sbcs/SBCS-Informatics
- ITS-research have said that money is required to do this (£250/tb)
  - I believe they misunderstood what this would be used for so perhaps contact them again and explain fully...

###Excel Spreadsheet
- Make just the product list editable
  - so that it is easier to use
  - i.e. you add number of units there and it automatically updates the list.

###IRYS
- Look at the possibility of mapping the Irys molecules to the raw reads…
  - BNX to CMAP (take a look at ref-aligner
- Archer Driving Test
  - Is it possible to run bionano analysis on archer might be a relevant approach?
    - [link]

### Galaxy Install
- RepeatExplorer is not working at all…
- Look at alternatives for galaxy set up
  - David Clayton & Conrad Bessant are interested in using Galaxy but are unable to do so.

### Add things learnt to YW/qmulcompute
- Scripts on how to analyse Scratch partitions
- ZSH set - How to use
- Lab servers - details on their resources (CPUs/ hyper threading etc.)

### Move .68 NUC (main master NUC) from library to Joseph Priestly server room…
- Richard Halford is currently on leave.
- Chris Walker has access to JP server server room.
  - Ask if we can gain access

### Set up Sys-init / tmux scripts for the nucs
- Set up systemd/upstart/sysv-init scripts or simply tux scripts.

### Redirect https://evolve.sbcs.qmul.ac.uk/wurm to https://wurmlab.github.io
- Ask Steve rostitor and find out who is system admin

## SCRIPTs to find files that can easily be run.
- More than 30 small files (i.e. <100kb) & haven’t been touched in 2 weeks
- Non-compressed, non-binary files that haven’t been touched in a month
- See `./scripts/big_txt_files` and `./scripts/directories_with_small_files` for sh files.
  - These need to be qsub'ed - SM11 scratch needs to be manually run on SM11

## Create Script that detects if users are misusing Archive Space
- When Archive space is set up, files will be backed up via rysnc.
- A script needs to be made that uses the rysnc log to determine if users are deleting files within days of writing then (and thus using the archival space as scratch space)


# USEFUL INFO

### With regards to SM11 internal scratch and SBCS-archive (storage1):
1. Are they backed up?
    >No, not as far as I know. They are scratch? Should they be? I'm not even sure what SBCS-Archive is there is no share of that name on storge1 I've just checked. The name (scratch) implies they are temporary transient files that would be very difficult to backup.

2. How often are they backed up?
    >We are trying to get /share/SBCS-Scratch (storage1) backed up daily to TSM currently, it used to be rsynced to gridpp (Other side of the server room) but this had to be restarted about a week ago, we are awaiting info from ITS Servers and Storage to get TSM working on storage1.

3. Where are they backed up to? (Offsite or Onsite where?)
    >TSM is based in DC1/DC2. Stoage1 and SM11 is in chemistry currently but will be moving to DC3 shortly.

4. Are tests in place to check that these storage systems are actually being backed up properly?
    >No. However we do check the TSM backup via EMail has occurred (correctly) and yes this email is read! and check files can be retrieved from time to time

5. Are tests in place to protect from potential faults in the backup system. e.g what safeguards are in place to protect from a RAID failure?
    >RAID 6 (9+2) (2 Parity Disks, with 2 Hot spare Disks)

### Lab Servers
#### Wurmlab
###### Nuc 68 (web server)
- Ip Address:
- Mac Address:

###### Nuc 69 (backup web server)
- Ip Address:
- Mac Address:


```sh
Add servers from other Labs on 5th Floor, if people want us to maintain them...
```

#### General
###### Prometheus (Experimental)
- Ip Address:
- Mac Address:

###### VM21 (Experimental)
- Ip Address:
- Mac Address:

###### VM22 (Experimental)
- Ip Address:
- Mac Address:

###### Sm11
- Ip Address:
- CPUS:
- Ram:
- Hyperthreading: false

###### General Apocrita
- Fat Nodes:
- Thin Nodes:

