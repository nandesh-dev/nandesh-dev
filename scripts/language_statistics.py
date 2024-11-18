import os
import pygame
import requests
import random
from datetime import datetime
from collections import defaultdict


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "<YOUR_GITHUB_TOKEN>")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "<YOUR_GITHUB_USERNAME>")

GITHUB_BASE_URL = "https://api.github.com"

LANGUAGE_EXTENSION_MAP = {
    "js": "js",
    "ts": "js",
    "jsx": "js",
    "tsx": "js",
    "go": "go",
    "rs": "rust",
    "py": "py",
}

LANGUAGE_COLOR_MAP = {
    "js": (211, 193, 57),
    "go": (57, 180, 211),
    "rust": (211, 103, 57),
    "py": (57, 142, 211),
}

MINIMUM_OPACITY = 8
MAXIMUM_OPACITY = 255

RANDOMNES = 5


BOX_SIZE = 24
GAP_SIZE = 4
MONTH_COUNT = 12 * 2

MAX_LINE_COUNT = 600


class Github:
    def __init__(self, username, token):
        self.username = username
        self.token = token

    def fetch_repositories(self):
        url = f"{GITHUB_BASE_URL}/users/{self.username}/repos"
        headers = {"Authorization": f"token {self.token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def fetch_commits(self, repo_name):
        url = f"{GITHUB_BASE_URL}/repos/{self.username}/{repo_name}/commits"
        headers = {"Authorization": f"token {self.token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def fetch_commit_details(self, repo_name, commit_sha):
        url = (
            f"{GITHUB_BASE_URL}/repos/{self.username}/{repo_name}/commits/{commit_sha}"
        )
        headers = {"Authorization": f"token {self.token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()


def main():
    pygame.init()

    github = Github(GITHUB_USERNAME, GITHUB_TOKEN)

    statistics = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))

    for repository in github.fetch_repositories():
        for commit in github.fetch_commits(repository["name"]):
            commit_date = datetime.fromisoformat(
                commit["commit"]["author"]["date"].replace("Z", "")
            )
            commit_dateint = commit_date.year * 12 + commit_date.month

            for file in github.fetch_commit_details(
                repository["name"], commit["sha"]
            ).get("files", []):
                file_extension = (
                    file["filename"].split(".")[-1]
                    if "." in file["filename"]
                    else "unknown"
                )

                language = LANGUAGE_EXTENSION_MAP.get(file_extension, None)

                if language != None:
                    lines_added = file.get("additions", 0)
                    statistics[language][commit_dateint][
                        commit_date.day // 8
                    ] += lines_added

    font = pygame.font.Font(None, 24)

    for language in statistics.keys():
        font_height = font.render("A", True, (0, 0, 0)).get_rect().height

        surface = pygame.Surface(
            (
                (BOX_SIZE + GAP_SIZE) * MONTH_COUNT + GAP_SIZE,
                (BOX_SIZE + GAP_SIZE) * 4 + 3 * GAP_SIZE + 2 * font_height,
            ),
            pygame.SRCALPHA,
        )

        current_date = datetime.now()
        current_dateint = current_date.year * 12 + current_date.month

        for i, dateint in enumerate(
            range(current_dateint - MONTH_COUNT, current_dateint)
        ):
            if dateint % 12 == 0:
                year_text = font.render(f"{dateint // 12}", True, (145, 152, 161))
                surface.blit(
                    year_text,
                    year_text.get_rect(
                        center=(
                            GAP_SIZE
                            + (GAP_SIZE + BOX_SIZE) * i
                            + year_text.get_rect().width // 2,
                            GAP_SIZE + font_height // 2,
                        )
                    ),
                )

            month_string = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"][
                dateint % 12
            ]

            month_text = font.render(month_string, True, (128, 128, 128, 128))
            surface.blit(
                month_text,
                month_text.get_rect(
                    center=(
                        GAP_SIZE + BOX_SIZE // 2 + (GAP_SIZE + BOX_SIZE) * i,
                        4 * BOX_SIZE + 6 * GAP_SIZE + font_height + font_height // 2,
                    )
                ),
            )

            stats = statistics[language].get(dateint, [0, 0, 0, 0])

            for w in range(4):
                randomness = RANDOMNES * random.random()
                opacity = min(
                    255,
                    round(
                        MINIMUM_OPACITY
                        + randomness
                        + (MAXIMUM_OPACITY - MINIMUM_OPACITY - randomness)
                        * stats[w]
                        / MAX_LINE_COUNT
                    ),
                )

                color = pygame.Color(
                    *LANGUAGE_COLOR_MAP.get(language, (255, 255, 255)), opacity
                )

                position = (
                    (BOX_SIZE + GAP_SIZE) * i + GAP_SIZE,
                    (BOX_SIZE + GAP_SIZE) * w + 2 * GAP_SIZE + font_height,
                )

                pygame.draw.rect(
                    surface,
                    color,
                    (*position, BOX_SIZE, BOX_SIZE),
                    border_radius=2,
                )

        pygame.image.save(surface, f"assets/language_statistics/{language}.png")

    pygame.quit()


if __name__ == "__main__":
    main()
