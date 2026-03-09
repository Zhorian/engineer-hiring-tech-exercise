#!/usr/bin/env python3
import crawler

"""Main entry point for the application."""

import argparse
from url_validator import validate_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A basic Python app")
    parser.add_argument("-u", "--url", help="The URL to process")
    args = parser.parse_args()

    if not args.url:
        print("No URL provided!")
        exit(1)

    if validate_url(args.url):
        print(f"Valid URL: {args.url}")
        crawler = crawler.Crawler()
        crawler.run(args.url)
    else:
        print(f"Invalid URL: {args.url}")