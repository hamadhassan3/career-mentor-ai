import React from 'react';

const CourseRecommendations = ({ courses, loadingCourses }) => {
  if (courses.length === 0) {
    return null;
  }

  return (
    <div className="border-t pt-4">
      <p className="text-xs font-medium text-gray-500 mb-2">Recommended Courses</p>
      {loadingCourses ? (
        <div className="flex items-center justify-center py-4">
          <svg className="animate-spin h-4 w-4 text-gray-400" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span className="ml-2 text-xs text-gray-500">Loading courses...</span>
        </div>
      ) : (
        <div className="space-y-2">
          {courses.slice(0, 3).map((course, index) => (
            <div
              key={index}
              onClick={() => {
                if (course.link) {
                  window.open(course.link, '_blank', 'noopener,noreferrer');
                } else {
                  console.error('No link found for course:', course);
                }
              }}
              className="block p-3 border border-gray-200 rounded-lg hover:border-indigo-300 hover:shadow-sm transition-all duration-200 animate-fade-in cursor-pointer"
              style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  {course.thumbnail ? (
                    <img 
                      src={course.thumbnail} 
                      alt={course.title}
                      className="w-16 h-12 object-cover rounded border"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div 
                    className={`w-16 h-12 bg-gradient-to-br from-indigo-100 to-purple-100 rounded border flex items-center justify-center ${course.thumbnail ? 'hidden' : 'flex'}`}
                  >
                    <svg className="w-6 h-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h5 className="text-sm font-medium text-gray-900 line-clamp-2 leading-tight">{course.title}</h5>
                  {course.instructor && (
                    <p className="text-xs text-gray-500 mt-1">by {course.instructor}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      course.platform === 'coursera' 
                        ? 'bg-blue-50 text-blue-600' 
                        : 'bg-purple-50 text-purple-600'
                    }`}>
                      {course.platform}
                    </span>
                    {course.rating && (
                      <span className="text-xs text-gray-500">★ {course.rating}</span>
                    )}
                    {course.level && (
                      <span className="text-xs text-gray-400">{course.level}</span>
                    )}
                  </div>
                </div>
                
                <div className="flex-shrink-0">
                  <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CourseRecommendations;