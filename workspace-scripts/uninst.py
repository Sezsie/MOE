import subprocess
import sys

def uninstall_all_packages():
    # Get a list of all installed packages
    result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=subprocess.PIPE)
    installed_packages = result.stdout.decode().splitlines()
    
    if not installed_packages:
        print("No packages to uninstall.")
        return

    # Uninstall each package
    print("Uninstalling all packages...")
    for package in installed_packages:
        package_name = package.split('==')[0]
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', package_name])
    print("All packages uninstalled.")

def install_requirements():
    # Install packages from requirements.txt
    print("Installing packages from requirements.txt...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    print("Installation complete.")

def main():
    uninstall_all_packages()
    install_requirements()

if __name__ == "__main__":
    main()
