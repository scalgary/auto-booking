# Code to book me to play Pickleball

This code manages my Pickleball booking and updates my calendar.

The main objective was to be able to book at exactly the opening time automatically using github action free tier (ie no warranty that the cron process will begin at exactly the requested time)
The second objective was to be able to update my personal calendar directly with my booking by looking at the gym website.

The learning objective was MLOps good practices:
- docker: production environement vs developement environment
- github actions: 
    - use of scheduling (cron) or manual
    - build docker image
    - execute code using arguments in a json file
    - bot to commit with tag
- safely managing secrets:
- reducing computing time
    - using bash in github action
    - limiting waiting time container


Python Learning:
- package selenium


-- Production
      image: scalgary/selenium-env:latest
      lighter image 
-- Development
      use image plus other packages in a container either on codespace or on local

-- Workflows:
   docker-build.yml manual for building image for production
   registrations.yml robust workflow for registration using execution.py and reminder.py
   clever_registration test workflow for registration using bot_execution.py and reminder.py

bot_execution vs execution --> use class instead of a bunch of functions
ideally needs a parent class to manage the driver and 2 children classes one for booking the slot and one for pulling out the appointments


