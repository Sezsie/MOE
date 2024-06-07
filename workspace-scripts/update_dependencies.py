import subprocess
import sys

############################################
# This script updates all installed packages
############################################

print("""
      ############################################
      # UPDATING ALL INSTALLED PACKAGES
      ############################################
      """)

def update_packages():
    # list all installed packages
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated'], capture_output=True, text=True)
    packages = [line.split()[0] for line in result.stdout.split('\n')[2:-1]]

    print("Checking for outdated packages...")

    if not packages:
        print("All packages are up to date.")
        return
    
    # show the user the list of outdated packages
    user_input = input(f"{len(packages)} packages are outdated. Do you want to update them? (y/n): ")
    
    # if user input is y, update the packages
    if user_input.lower() != 'y':
        print("Exiting without updating packages.")
        return


    print("Updating packages:")
    for package in packages:
        print(f"Updating {package}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', package])

if __name__ == "__main__":
    update_packages()
