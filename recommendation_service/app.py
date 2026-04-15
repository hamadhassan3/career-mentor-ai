import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from scrapers.scraper_factory import ScraperFactory

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Course recommendation service is running',
        'available_platforms': ScraperFactory.get_available_platforms()
    })


@app.route('/platforms', methods=['GET'])
def get_platforms():
    """Get available platforms"""
    return jsonify({
        'platforms': ScraperFactory.get_available_platforms()
    })


@app.route('/courses/coursera', methods=['POST'])
def search_coursera():
    """Search courses on Coursera"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        scraper = ScraperFactory.get_scraper('coursera')
        courses = scraper.search_courses(query, limit)

        for course in courses:
            course['platform'] = 'coursera'

        return jsonify({
            'platform': 'coursera',
            'query': query,
            'total_results': len(courses),
            'courses': courses
        })

    except Exception as e:
        logger.error("Error in Coursera search: %s", str(e))
        return jsonify({'error': 'Internal server error'}), 500



@app.route('/courses/youtube', methods=['POST'])
def search_youtube():
    """Search course playlists on YouTube"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        scraper = ScraperFactory.get_scraper('youtube')
        courses = scraper.search_courses(query, limit)

        for course in courses:
            course['platform'] = 'youtube'

        return jsonify({
            'platform': 'youtube',
            'query': query,
            'total_results': len(courses),
            'courses': courses
        })

    except Exception as e:
        logger.error("Error in YouTube search: %s", str(e))
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/courses/search', methods=['POST'])
def search_courses():
    """Search courses across multiple platforms"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        platforms = data.get('platforms', ['coursera', 'youtube'])
        limit = data.get('limit', 10)

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        results = []
        platform_results = {}

        for platform in platforms:
            try:
                scraper = ScraperFactory.get_scraper(platform)
                courses = scraper.search_courses(query, limit)

                for course in courses:
                    course['platform'] = platform
                    results.append(course)

                platform_results[platform] = {
                    'count': len(courses),
                    'courses': courses
                }

            except Exception as e:
                logger.error("Error scraping %s: %s", platform, str(e))
                platform_results[platform] = {
                    'count': 0,
                    'error': str(e),
                    'courses': []
                }
                continue

        return jsonify({
            'query': query,
            'total_results': len(results),
            'platforms_searched': platforms,
            'platform_breakdown': platform_results,
            'courses': results
        })

    except Exception as e:
        logger.error("Error in search_courses: %s", str(e))
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)