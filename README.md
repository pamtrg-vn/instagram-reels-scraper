# Instagram Reels Scraper

This project provides a Python script to scrape Instagram Reels data for a specific user. It allows you to fetch reels, apply filters, and extract relevant information.

## Setup

### Prerequisites

- Python 3.7 or higher

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/pamtrg-vn/instagram-reels-scraper.git
   cd instagram-reels-scraper
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

The main script is `reels.py`. Here's an example of how to use it:

```python
# python reels.py --userid 31051275986 --limit 50 --min-likes 1000 --min-views 10000
python reels.py --userid <instagram_user_id> --limit <limit> --min-likes <min_likes> --min-views <min_views>
```

### Command-line Arguments

- `--userid`: Instagram userid to scrape reels from (required)
- `--limit`: Maximum number of reels to fetch (default: 20)
- `--min-likes`: Minimum number of likes for a reel to be included (default: 0)
- `--min-views`: Minimum number of views for a reel to be included (default: 0)

## Output

The script will generate a JSON file named `<userid>_reels.json` in the current directory. This file will contain an array of reel objects, each with the following information:

- `id`: Unique identifier of the reel
- `shortcode`: Instagram shortcode for the reel
- `timestamp`: Timestamp of when the reel was posted
- `caption`: Caption of the reel
- `likes`: Number of likes
- `views`: Number of views
- `video_url`: Direct URL to the video file

## Limitations

- This script uses web scraping techniques and may break if Instagram changes its website structure.
- Excessive use may lead to your IP being temporarily blocked by Instagram.
- This tool is for educational purposes only. Be sure to comply with Instagram's terms of service and respect user privacy.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
