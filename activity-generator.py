#!/usr/bin/env python
import os
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen, PIPE
import time
import sys

ASCII_ART = r"""
       /\_____/\   
      /  o   o  \  
     ( ==  ^  == ) 
      )         (  
     (           ) 
    ( (  )   (  ) )
   (__(__)___(__)__)
    
Fake it till you make it! 🚀
"""

def print_colorful(text, color='\033[92m'):
    """Print text in color"""
    ENDC = '\033[0m'
    print(f"{color}{text}{ENDC}")

def loading_animation(duration=2):
    """Display a loading animation"""
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{animation[i]} Processing...")
        sys.stdout.flush()
        time.sleep(0.1)
        i = (i + 1) % len(animation)
    sys.stdout.write("\r" + " " * 20 + "\r")

def get_validated_input(prompt, input_type=str, min_val=None, max_val=None):
    """Get and validate user input"""
    while True:
        try:
            user_input = input_type(input(prompt))
            if min_val is not None and user_input < min_val:
                print_colorful(f"Value must be at least {min_val}!", '\033[91m')
                continue
            if max_val is not None and user_input > max_val:
                print_colorful(f"Value must be no more than {max_val}!", '\033[91m')
                continue
            return user_input
        except ValueError:
            print_colorful("Invalid input! Please try again.", '\033[91m')

def main():
    print_colorful(ASCII_ART)
    print_colorful("Welcome to the GitHub Contribution Generator! 🎮\n")

    # Get repository information
    repository = input("Enter your repository URL (e.g. git@github.com:user/repo.git): ")
    
    # Get year with validation
    current_year = datetime.now().year
    year = get_validated_input(
        f"Enter the year for contribution generation: ",
        int,
        current_year-5,
        current_year+1
    )

    # Get commit parameters with validation
    max_commits = get_validated_input(
        "Enter the maximum number of commits per day (1-20): ",
        int,
        1,
        20
    )
    
    frequency = get_validated_input(
        "Enter commit frequency (0-100): ",
        int,
        0,
        100
    )

    # Weekend preference
    while True:
        no_weekends_input = input("Generate activity on weekends? (y/n): ").lower()
        if no_weekends_input in ['y', 'n']:
            break
        print_colorful("Please enter 'y' or 'n'!", '\033[91m')

    no_weekends = no_weekends_input != 'y'

    print_colorful("\n🚀 Initializing repository...", '\033[94m')
    loading_animation()

    # Create directory
    curr_date = datetime.now()
    directory = 'repository-' + curr_date.strftime('%Y-%m-%d-%H-%M-%S')
    
    if repository:
        start = repository.rfind('/') + 1
        end = repository.rfind('.')
        base_directory = repository[start:end]
        directory = f"{base_directory}-{year}"
        counter = 1
        while os.path.exists(directory):
            directory = f"{base_directory}-{year}-{counter}"
            counter += 1
    
    os.mkdir(directory)
    os.chdir(directory)
    run(['git', 'init', '-b', 'main'])

    print_colorful("\n🌱 Generating commit history...", '\033[94m')
    
    # Generate commits
    start_date = curr_date.replace(year=year, hour=20, minute=0)
    total_commits = 0
    
    for day in (start_date + timedelta(n) for n in range(365)):
        if (not no_weekends or day.weekday() < 5) and randint(0, 100) < frequency:
            daily_commits = contributions_per_day(max_commits)
            total_commits += daily_commits
            for commit_time in (day + timedelta(minutes=m) for m in range(daily_commits)):
                contribute(commit_time)
                sys.stdout.write(f"\rCommits generated: {total_commits}")
                sys.stdout.flush()

    print_colorful(f"\n\n✨ Generated {total_commits} commits successfully!", '\033[92m')

    if repository:
        print_colorful("\n📤 Pushing to remote repository...", '\033[94m')
        loading_animation()
        try:
            run(['git', 'remote', 'add', 'origin', repository])
            result = run(['git', 'push', '-f', '-u', 'origin', 'main'])
            if result.returncode != 0:  # Check if push failed
                print_colorful("\n⚠️ Unable to push to repository. Please:", '\033[93m')
                print_colorful("1. Verify the repository exists at: " + repository, '\033[93m')
                print_colorful("2. Check if you have the correct write permissions", '\033[93m')
                print_colorful("3. Ensure your SSH key is properly configured", '\033[93m')
                print_colorful("\nYour commits are saved locally at: " + os.getcwd(), '\033[93m')
            else:
                print_colorful("\n🎉 Repository successfully pushed to GitHub!", '\033[92m')
        except Exception as e:
            print_colorful("\n⚠️ Push failed. Please:", '\033[93m')
            print_colorful("1. Verify the repository exists at: " + repository, '\033[93m')
            print_colorful("2. Check if you have the correct write permissions", '\033[93m')
            print_colorful("3. Ensure your SSH key is properly configured", '\033[93m')
            print_colorful("\nYour commits are saved locally at: " + os.getcwd(), '\033[93m')
    
    if year == current_year:
        print_colorful("Note: If you had previous contributions this year, they have been overwritten.", '\033[93m')

def contribute(date):
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date),
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])

def run(commands):
    process = Popen(commands, stdout=PIPE, stderr=PIPE)
    process.wait()
    return process  # Return the process object to check return code

def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')

def contributions_per_day(max_commits):
    return randint(1, max_commits)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colorful("\n\n❌ Process interrupted by user", '\033[91m')
    except Exception as e:
        print_colorful(f"\n\n❌ An error occurred: {str(e)}", '\033[91m')