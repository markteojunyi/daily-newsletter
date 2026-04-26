from database import mark_seen
from fetcher import fetch_stories
from sender import send_newsletter
from writer import write_newsletter


def run():
    print("Starting Newsletter Agent...\n")

    stories = fetch_stories()
    if not stories:
        print("No new stories found. Exiting.")
        return

    newsletter = write_newsletter(stories)
    print("\nNewsletter ready.")
    print("-" * 40)
    print(newsletter)
    print("-" * 40 + "\n")

    send_newsletter(newsletter_text=newsletter, topic="AI & Technology")

    # Persist after a successful send so a failed send doesn't poison the DB.
    mark_seen(stories)
    print("\nDone!")


if __name__ == "__main__":
    run()
