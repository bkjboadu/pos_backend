#!/bin/bash

echo "checking out to the main branch"
git checkout master

echo "Resetting local main branch to match origin/main"
git reset --hard origin/master

echo "Force pushing to heroku main ..."
git push heroku master --force

echo "deployment to heroku completed successfully"
