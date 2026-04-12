from fetcher import fetch_stories
from sender import send_newsletter
from writer import write_newsletter


def run():
    print("Starting Newsletter Agent...\n")

    stories = fetch_stories()
    if not stories:
        print("No stories found. Exiting.")
        return

    newsletter = write_newsletter(stories)
    print("\nNewsletter ready.")
    print("-" * 40)
    print(newsletter)
    print("-" * 40 + "\n")

    send_newsletter(newsletter_text=newsletter, topic="AI & Technology")
    print("\nDone!")


if __name__ == "__main__":
    run()
