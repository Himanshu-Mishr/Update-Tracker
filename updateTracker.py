import os, subprocess

# Global variables
EXCLUDE_FOLDERS = ["node_modules", "bower_components", ".git", "uploads"]
PRESENT_DIRECTORY = "."


def get_git_repo_path():
	git_repo_dir_list = []

	# traverse root directory, and list directories as dirs and files as files
	for root, dirs, files in os.walk(PRESENT_DIRECTORY):

		# excluding folder that don't need to traversed
		dirs[:] = [d for d in dirs if d not in EXCLUDE_FOLDERS]

		process = subprocess.Popen(["git", "-C", root, "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = process.communicate()

		# exit on error
		if err:
			print("Error while traversing directories.")
			exit(1)

		# bytes to string
		out = str(out)

		# stripping whitespaces
		out = out.rstrip()
		out = out.lstrip()
		git_repo_dir_list.append(out)

	# removing duplicates
	git_repo_dir_list = list(set(git_repo_dir_list))
	return git_repo_dir_list

def get_remote_name_dict(path_list):
	adict = {}
	for path in path_list:
		process = subprocess.Popen(["git", "-C", path, "remote", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = process.communicate()

		# stripping whitespaces
		out = out.rstrip()
		out = out.lstrip()

		remote_list = []
		remote_name_list = []
		if out != '':
			remote_list = out.split("\n")

		if len(remote_list) != 0:
			for aremote in remote_list:
				aremote_list = aremote.split()
				remote_name_list.append(aremote_list[0])
			remote_name_list = list(set(remote_name_list))
			adict[path] = remote_name_list
		else:
			adict[path] = []

	return adict

def print_repo_status(repo_path, remote_name_list):
	print(repo_path)
	if len(remote_name_list):

		for remote_name in remote_name_list:
			# git fetch remote_name
			step1_process = subprocess.Popen(["git", "-C", repo_path, "fetch", remote_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			step1_out, step1_err = step1_process.communicate()

			step2_process = subprocess.Popen(["git", "-C", repo_path, "log", "HEAD.." + remote_name + "/master", "--oneline", "--pretty=format:%h%x09%an"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			step2_out, step2_err = step2_process.communicate()

			diff_count = len(step2_out.split("\n"))
			if step2_out.split("\n")[0] == '':
				diff_count = 0

			if not (len(remote_name) >= 20):
				remote_name = remote_name + (20 - len(remote_name)) * " "

			if diff_count:
				print(remote_name + " : \033[0;42m " +  str(diff_count) + " commit \033[0m")
			else:
				print(remote_name + " : \033[0;44m " +  str(diff_count) + " commit \033[0m")
	else :
		print("\033[0;31m No remote name for this repo \033[0m")
	print("------------------------------------------------------------------")


def updateTracker():

	git_repo_dir_list = get_git_repo_path()
	git_repo_dir_list.sort()

	remote_dict = get_remote_name_dict(git_repo_dir_list)
	# print(remote_dict.keys())
	for repo in remote_dict.keys():
		print_repo_status(repo, remote_dict[repo])

	return 0


if __name__ == '__main__':
	updateTracker()
