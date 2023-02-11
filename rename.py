"""Rename all the files in the library to the format SXXEXX"""


import os
import re
import shutil

LIBRARY_PATH = "/home/vistamar/telegram-bot/"

# iterate over all the directories inside the library_path
for folder in os.listdir(os.getcwd()):
    if (
        os.path.isdir(os.path.join(os.getcwd(), folder))
        and not folder.startswith(".")
        and not folder.startswith("_")
    ):
        for season in os.listdir(os.path.join(os.getcwd(), folder)):
            if season.startswith("Season"):
                for episode in os.listdir(os.path.join(os.getcwd(), folder, season)):
                    if os.path.isdir(
                        os.path.join(os.getcwd(), folder, season, episode)
                    ):
                        for episode_folder in os.listdir(
                            os.path.join(os.getcwd(), folder, season, episode)
                        ):
                            for file in os.listdir(
                                os.path.join(
                                    os.getcwd(), folder, season, episode, episode_folder
                                )
                            ):
                                if (
                                    file.endswith(".mp4")
                                    or file.endswith(".mkv")
                                    or file.endswith(".avi")
                                ):
                                    n_season = int(
                                        re.search(r"(\d+)-(\d+)", episode).group(1)
                                    )
                                    n_episode = int(
                                        re.search(r"(\d+)-(\d+)", episode).group(2)
                                    )
                                    extension = os.path.splitext(file)[1]
                                    # rename the file to the format SXXEXX
                                    new_name = f"{folder} S{n_season:02d}E{n_episode:02d}{extension}"
                                    os.rename(
                                        os.path.join(
                                            os.getcwd(),
                                            folder,
                                            season,
                                            episode,
                                            episode_folder,
                                            file,
                                        ),
                                        os.path.join(
                                            os.getcwd(), folder, season, new_name
                                        ),
                                    )
                                    shutil.rmtree(
                                        os.path.join(
                                            os.getcwd(), folder, season, episode
                                        ),
                                        ignore_errors=True,
                                    )
