#!/usr/bin/env python3
"""
Command-line interface for the universal documentation crawler.
This provides a more convenient way to run the doc_crawler spider.
"""

import argparse
import os
import sys
from urllib.parse import urlparse
from scrapy.cmdline import execute

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8 compatibility
    import pkg_resources

    def version(package_name):
        try:
            return pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            return None

    PackageNotFoundError = pkg_resources.DistributionNotFound


def get_version():
    try:
        return version("html_docs_crawler")
    except PackageNotFoundError:
        return "unknown"


def get_domain_from_url(url):
    """Extract domain from a URL string."""
    parsed = urlparse(url)
    domain = parsed.netloc
    if not domain:
        return "unknown_domain"
    # Remove port if present
    if ":" in domain:
        domain = domain.split(":")[0]
    return domain


def get_default_output_dir(start_urls):
    """Generate default output directory based on the first start URL."""
    if not start_urls:
        return "markdown_output"

    # Use the first URL to determine domain
    first_url = start_urls.split(",")[0].strip()
    domain = get_domain_from_url(first_url)

    # Build path: ~/.config/doc_crawler/_docs/{domain}
    home = os.path.expanduser("~")
    return os.path.join(home, ".config", "doc_crawler", "_docs", domain)


def main():
def show_llms_txt():
    llms_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "llms.txt")
    try:
        with open(llms_txt_path, encoding="utf-8") as f:
            sys.stdout.write(f.read())
    except FileNotFoundError:
        print(f"llms.txt not found at {llms_txt_path}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Universal documentation crawler: Convert HTML pages to Markdown with internal link correction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
LLM users: run 'doc_crawler --llm-help' for the full LLM-optimized guide (llms.txt).
Examples:
  doc_crawler --start-urls https://akshare.akfamily.xyz --allowed-domains akshare.akfamily.xyz
  doc_crawler --start-urls https://opencode.ai/docs/zh-cn/ --allow-paths /docs/zh-cn/
  doc_crawler --start-urls https://build123d.readthedocs.io/en/stable/ --single-page
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show version information and exit",
    )

    parser.add_argument(
        "--llm-help",
        action="store_true",
        help="Print the full LLM-optimized usage guide from llms.txt and exit",
    )

    # Required arguments
    parser.add_argument(
        "--start-urls", required=True, help="Starting URLs (comma-separated)"
    )

    # Optional arguments matching the spider's parameters
    parser.add_argument(
        "--allowed-domains", default="", help="Allowed domains (comma-separated)"
    )

    parser.add_argument(
        "--deny-patterns", default="", help="Regex patterns to deny (comma-separated)"
    )

    parser.add_argument(
        "--allow-paths", default="", help="Path prefixes to allow (comma-separated)"
    )

    parser.add_argument(
        "--body-selector",
        default="main, article, .content, .document, .body, body",
        help="CSS selector for HTML body content",
    )

    parser.add_argument(
        "--output-dir",
        default="",
        help="Output directory for Markdown files (default: ~/.config/doc_crawler/_docs/{domain})",
    )

    parser.add_argument(
        "--converter-engine",
        default="markitdown",
        choices=["markitdown", "html2text"],
        help="Converter engine: 'markitdown' (default) or 'html2text'",
    )

    parser.add_argument(
        "--single-page",
        default="false",
        choices=["true", "false"],
        help="Single page mode (don't follow links)",
    )

    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level",
    )

    # Handle --llm-help before parsing to avoid required argument error
    if "--llm-help" in sys.argv:
        show_llms_txt()

    args = parser.parse_args()

    # Determine output directory
    if not args.output_dir:
        args.output_dir = get_default_output_dir(args.start_urls)
    # Expand user directory (~)
    args.output_dir = os.path.expanduser(args.output_dir)
    # Convert to absolute path before chdir
    args.output_dir = os.path.abspath(args.output_dir)
    # Ensure the directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Change to the directory containing scrapy.cfg
    # This is necessary for scrapy to find the project settings
    # The cli.py file is in doc_crawler/, so go up one level to find scrapy.cfg
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # doc_crawler/ -> project root

    # Check if scrapy.cfg exists in the project root
    scrapy_cfg_path = os.path.join(project_root, "scrapy.cfg")
    if os.path.exists(scrapy_cfg_path):
        os.chdir(project_root)
    else:
        # If not found, try the parent directory
        parent_dir = os.path.dirname(project_root)
        scrapy_cfg_path = os.path.join(parent_dir, "scrapy.cfg")
        if os.path.exists(scrapy_cfg_path):
            os.chdir(parent_dir)
        else:
            print(
                f"警告: 未找到 scrapy.cfg 文件，当前目录: {os.getcwd()}",
                file=sys.stderr,
            )

    # Build scrapy command arguments
    scrapy_args = [
        "scrapy",
        "crawl",
        "doc_crawler",
        "-a",
        f"start_urls={args.start_urls}",
        "-a",
        f"allowed_domains={args.allowed_domains}",
        "-a",
        f"deny_patterns={args.deny_patterns}",
        "-a",
        f"allow_paths={args.allow_paths}",
        "-a",
        f"body_selector={args.body_selector}",
        "-a",
        f"output_dir={args.output_dir}",
        "-a",
        f"converter_engine={args.converter_engine}",
        "-a",
        f"single_page={args.single_page}",
        "--loglevel",
        args.loglevel,
    ]

    # Execute scrapy command
    sys.exit(execute(scrapy_args))


if __name__ == "__main__":
    main()
