# Collimundo


## Git commands

**Clone:** Clone git hub repository \
`git clone (git link)`

**Switch branch:** Switch branch to different branch. Use -b to create a new branch if this branch does not yet exist. This will create branch from starting current commit. \
`git checkout [-b (IF new branch)]  (target branch) [source branch (IF new branch)]` \
or `git checkout (target branch)`

**Add:** Add files to git. Use . to add everything or use specific names to only add certain files. \
`git add .`

**Commit:** Create a new commit. Use -m to change the commit name. \
`git commit -m "(commit message)"`

**Merge:** To merge a branch to another branch. Switch to the branch you to want to merge to and then merge the other branch into this one. Example below merges branch “feature” into the branch “develop”. **! Always keep --no-ff so the merging gets done in a new commit object !** \
`git checkout develop` \
`git merge --no-ff (feature)`

**Push:** Push (a certain branch) to GitHub/GitLab. If this also pushes a new branch then you need to add --set-upstream. \
`git push [--set-upstream] origin [branch]`

**Pull:** Pull (a certain branch) from GitHub/GitLab. This automatically merges files. \
`git pull`

**Branch status:** Get current branch and all branches in git. \
`git branch` \
"Create new branch \
`git branch (target branch)` \
or `git checkout -b (target branch) (source branch)`

**Delete branch:** Delete branch. -d to delete fully merged branch. -D to delete a none fully merged branch. \
`git branch -d  (target branch)` \
`git branch -D (target branch)`

**Git status:** Get the status of git. This also shows unadded files. \
`git status`



## Branching strategy

### Feature
**May branch off from:** develop \
**Must merge back into:** develop \
**Branch naming convention:** anything except main, develop, release-\*, or hotfix-\* \
A feature branch is a branch were one feature gets developed after which it will get merged into the main branch.

**Creating a feature branch**
```
git checkout -b myfeature develop
```

**Incorporating a finished feature on develop**
```
git checkout develop
git merge --no-ff myfeature
git push origin develop
```

### Release
**May branch off from:** develop \
**Must merge back into:** develop and main \
**Branch naming convention:** release-\* \
When development branch contains all features needed for the next release you can start a release branch. Here the last needed changes can be made before merging it into the main branch.

**Creating a release branch (examples with version 1.2)**
```
git checkout -b release-1.2 develop
./bump-version.sh 1.2 # if this file exist
git commit -a -m "Bumped version number to 1.2"
```
**Finishing a release branch (examples with version 1.2)** \
Merge feature branch into the main branch and change tag to new version number.
```
git checkout main
git merge --no-ff release-1.2
git tag -a 1.2
```
Merge changes into development as well as some changes were made in the feature branch.
```
$ git checkout develop
$ git merge --no-ff release-1.2
```

### Hotfix
**May branch off from:** main \
**Must merge back into:** develop and main \
**Branch naming convention:** hotfix-\* \
When a problem gets found in the current release that needs to be changed quickly one should start from this last release in the main branch and make the required changes.

**Creating the hotfix branch (examples last version was 1.2)**
```
git checkout -b hotfix-1.2.1 main
./bump-version.sh 1.2.1 # if this file exist
git commit -a -m "Bumped version number to 1.2.1"
```
Fix the problem and then commit.
```
$ git commit -m "Fixed severe production problem"
```
**Finishing a hotfix branch (examples last version was 1.2)** \
Update the main branch and change tag to new version number.
```
git checkout main
git merge --no-ff hotfix-1.2.1
git tag -a 1.2.1
```
Also update the development branch
```
git checkout develop
git merge --no-ff hotfix-1.2.1
```

If a release branch currently exists merge into the release branch instead. The release branch will later on be merged into the development branch so the hotfix will happen. If the hotfix is required immediately in the development branch then it should be merged into both.



## Web Application via Django (folder Collimundo)

**Install** `python -m pip install Django==5.0.2`\
**Run localy** `python manage.py runserver`

### Apps

An app provides a certain functionality. It is used to break up the code in different smaller components.

Apps in this project:
- **Dashboard:** Dashboard and widgets
- ...




## CI/CD

### Testing
Writing testing pipelines is done in the *.gitlab-ci.yml* file. A nice tutorial is available at [Continuous Integration / Continuous Development (CI/CD) (hsf-training.github.io)](https://hsf-training.github.io/hsf-training-cicd/).

Example *.gitlab-ci.yml* file (source: [(hsf-training.github.io)](https://hsf-training.github.io/hsf-training-cicd/)):
In this example there is a skim.cxx file. Every time this file gets changed the test build_skim is run. This test first sets up a conda. This is done in before_script so it does not need to be done every single time. Then script contains the actual test. In this case it is just the compiling of the file skim.cxx. The success or possible failure of this test will be visible on GitLab under the tab pipelines.

```
build_skim:
	before_script:
		- wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux
			x86_64.sh -O ~/miniconda.sh
 		- bash ~/miniconda.sh -b -p $HOME/miniconda
		- eval "$(~/miniconda/bin/conda shell.bash hook)"
		- conda init
	script:
		- conda install root=6.28 --yes
		- COMPILER=$(root-config --cxx)
		- FLAGS=$(root-config --cflags --libs)
		- $COMPILER -g -O3 -Wall -Wextra -Wpedantic -o skim skim.cxx $FLAGS
	only:
		changes:
      			- skim.cxx
```

On every push all tests get run depending on their Only tag.


### Continuous delivery
This is also done via the .gitlab-ci.yml pipeline. By default, GitLab CI/CD retains job artifacts for the last successful pipeline. These can be accessed under the "Pipeline" section.

### Continuous deployement
Pull the main branch at regular times using for example crontab.\
As an extra option the development branch could be pulled in the same way and made available through a different url for testing purposes.
