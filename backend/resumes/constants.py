"""
Skills categorization constants for resume processing.
"""

IT_SKILLS = {
    'Programming Languages': [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'Go', 'Rust',
        'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Dart',
        'Objective-C', 'Visual Basic', 'Assembly', 'Haskell', 'Clojure', 'F#',
        'Groovy', 'Lua', 'Julia', 'Erlang', 'Elixir'
    ],
    'Web Technologies': [
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js',
        'Django', 'Flask', 'Spring', 'Laravel', 'CodeIgniter', 'Symfony',
        'ASP.NET', 'jQuery', 'Bootstrap', 'Sass', 'Less', 'Webpack', 'Gulp',
        'Grunt', 'Ember.js', 'Backbone.js', 'Svelte', 'Next.js', 'Nuxt.js',
        'Gatsby', 'GraphQL', 'REST API', 'SOAP', 'XML', 'JSON'
    ],
    'Databases': [
        'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Oracle', 'SQL Server',
        'Redis', 'Cassandra', 'DynamoDB', 'CouchDB', 'Neo4j', 'Firebase',
        'MariaDB', 'Amazon RDS', 'Elasticsearch', 'InfluxDB', 'TimescaleDB',
        'SQL', 'NoSQL', 'Database Design', 'Database Administration'
    ],
    'Cloud & DevOps': [
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
        'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible', 'Chef', 'Puppet',
        'Vagrant', 'CI/CD', 'DevOps', 'Microservices', 'Serverless',
        'Lambda', 'EC2', 'S3', 'CloudFormation', 'Helm', 'Istio',
        'Prometheus', 'Grafana', 'ELK Stack', 'Nginx', 'Apache'
    ],
    'Data Science & AI': [
        'Machine Learning', 'Deep Learning', 'Artificial Intelligence',
        'Data Science', 'Data Analysis', 'Statistics', 'Pandas', 'NumPy',
        'Scikit-learn', 'TensorFlow', 'PyTorch', 'Keras', 'OpenCV',
        'Natural Language Processing', 'Computer Vision', 'Big Data',
        'Apache Spark', 'Hadoop', 'Kafka', 'Tableau', 'Power BI',
        'Jupyter', 'R Studio', 'SPSS', 'SAS', 'Neural Networks'
    ],
    'Mobile Development': [
        'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
        'Cordova', 'PhoneGap', 'Swift', 'Kotlin', 'Objective-C',
        'Mobile Development', 'App Development'
    ],
    'Testing & QA': [
        'Unit Testing', 'Integration Testing', 'Test Automation', 'Selenium',
        'Jest', 'Mocha', 'Cypress', 'TestNG', 'JUnit', 'PyTest',
        'Quality Assurance', 'Manual Testing', 'Performance Testing',
        'Load Testing', 'Security Testing', 'API Testing', 'Postman'
    ],
    'Version Control & Tools': [
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial',
        'JIRA', 'Confluence', 'Slack', 'Trello', 'Asana', 'VS Code',
        'IntelliJ IDEA', 'Eclipse', 'Visual Studio', 'Sublime Text',
        'Atom', 'Vim', 'Emacs'
    ],
    'Operating Systems': [
        'Linux', 'Ubuntu', 'CentOS', 'Red Hat', 'Debian', 'Windows',
        'macOS', 'Unix', 'FreeBSD', 'Windows Server', 'System Administration'
    ],
    'Security': [
        'Cybersecurity', 'Information Security', 'Network Security',
        'Penetration Testing', 'Ethical Hacking', 'Cryptography',
        'SSL/TLS', 'OAuth', 'JWT', 'OWASP', 'Firewall', 'VPN',
        'Security Audit', 'Vulnerability Assessment'
    ],
    'Networking': [
        'TCP/IP', 'HTTP/HTTPS', 'DNS', 'DHCP', 'Network Administration',
        'Routing', 'Switching', 'Load Balancing', 'CDN', 'VPN',
        'Network Security', 'Cisco', 'Juniper'
    ],
    'Business Intelligence': [
        'Business Intelligence', 'Data Warehousing', 'ETL', 'OLAP',
        'Data Mining', 'Reporting', 'Analytics', 'KPI', 'Dashboards',
        'Business Analysis', 'Requirements Analysis'
    ]
}

SOFT_SKILLS = {
    'Communication': [
        'Communication', 'Verbal Communication', 'Written Communication', 'Presentation Skills',
        'Public Speaking', 'Active Listening', 'Storytelling', 'Negotiation',
        'Interpersonal Skills', 'Cross-cultural Communication', 'Business Writing',
        'Technical Writing', 'Documentation', 'Reporting', 'Email Etiquette'
    ],
    'Leadership & Management': [
        'Leadership', 'Team Leadership', 'Project Management', 'People Management',
        'Strategic Planning', 'Decision Making', 'Delegation', 'Mentoring',
        'Coaching', 'Conflict Resolution', 'Change Management', 'Risk Management',
        'Resource Management', 'Budget Management', 'Stakeholder Management'
    ],
    'Collaboration & Teamwork': [
        'Teamwork', 'Collaboration', 'Team Building', 'Cross-functional Collaboration',
        'Relationship Building', 'Networking', 'Partnership Development',
        'Consensus Building', 'Team Player', 'Cooperative', 'Supportive'
    ],
    'Problem Solving & Critical Thinking': [
        'Problem Solving', 'Critical Thinking', 'Analytical Thinking', 'Logical Thinking',
        'Creative Thinking', 'Innovation', 'Troubleshooting', 'Root Cause Analysis',
        'Decision Analysis', 'Strategic Thinking', 'Systems Thinking',
        'Research Skills', 'Data-driven Decision Making'
    ],
    'Personal Effectiveness': [
        'Time Management', 'Organization', 'Prioritization', 'Multi-tasking',
        'Self-motivated', 'Initiative', 'Proactive', 'Detail-oriented',
        'Results-oriented', 'Goal-oriented', 'Deadline Management',
        'Work Independently', 'Self-starter', 'Productivity', 'Efficiency'
    ],
    'Adaptability & Learning': [
        'Adaptability', 'Flexibility', 'Quick Learner', 'Continuous Learning',
        'Growth Mindset', 'Resilience', 'Open-minded', 'Agile', 'Versatile',
        'Change Adaptation', 'Learning Agility', 'Curiosity', 'Self-improvement'
    ],
    'Emotional Intelligence': [
        'Emotional Intelligence', 'Empathy', 'Self-awareness', 'Social Awareness',
        'Emotional Regulation', 'Stress Management', 'Patience', 'Compassion',
        'Understanding', 'Interpersonal Awareness', 'Cultural Sensitivity'
    ],
    'Professional & Ethics': [
        'Professional', 'Work Ethic', 'Integrity', 'Accountability', 'Responsibility',
        'Reliability', 'Dependable', 'Trustworthy', 'Ethical', 'Confidentiality',
        'Commitment', 'Dedication', 'Punctual', 'Honest', 'Transparent'
    ],
    'Customer & Client Focus': [
        'Customer Service', 'Client Relations', 'Customer Focus', 'Client Management',
        'Customer Success', 'Service-oriented', 'Customer Satisfaction',
        'Client Communication', 'Account Management', 'Customer Experience',
        'Complaint Resolution', 'Customer Support'
    ],
    'Creativity & Innovation': [
        'Creative', 'Innovative', 'Imagination', 'Brainstorming', 'Ideation',
        'Design Thinking', 'Out-of-the-box Thinking', 'Conceptualization',
        'Artistic', 'Inventive', 'Original Thinking', 'Entrepreneurial'
    ]
}

LANGUAGE_SKILLS = {
    'English Languages': [
        'English', 'Business English', 'Technical English', 'English Proficiency',
        'English Writing', 'English Speaking', 'English Communication'
    ],
    'Asian Languages': [
        'Hindi', 'Mandarin', 'Chinese', 'Japanese', 'Korean', 'Tamil', 'Telugu',
        'Kannada', 'Malayalam', 'Bengali', 'Gujarati', 'Marathi', 'Punjabi',
        'Urdu', 'Sanskrit', 'Thai', 'Vietnamese', 'Indonesian', 'Malay',
        'Tagalog', 'Filipino'
    ],
    'European Languages': [
        'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Dutch',
        'Russian', 'Polish', 'Swedish', 'Norwegian', 'Danish', 'Finnish',
        'Greek', 'Turkish', 'Czech', 'Hungarian', 'Romanian', 'Bulgarian',
        'Croatian', 'Serbian', 'Ukrainian'
    ],
    'Middle Eastern Languages': [
        'Arabic', 'Hebrew', 'Persian', 'Farsi', 'Kurdish', 'Pashto'
    ],
    'African Languages': [
        'Swahili', 'Zulu', 'Yoruba', 'Hausa', 'Amharic', 'Somali'
    ],
    'Sign Languages': [
        'Sign Language', 'ASL', 'American Sign Language', 'BSL',
        'British Sign Language', 'ISL', 'Indian Sign Language'
    ],
    'Language Proficiency Levels': [
        'Native', 'Fluent', 'Proficient', 'Intermediate', 'Conversational',
        'Basic', 'Beginner', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2',
        'TOEFL', 'IELTS', 'TOEIC', 'Cambridge English'
    ]
}