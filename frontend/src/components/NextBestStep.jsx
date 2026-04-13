import React, { useState } from 'react';
import { resumeAPI } from '../config/api-resume-processor';

const NextBestStep = ({ resumeData, targetDesignation }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateRecommendations = async () => {
    setLoading(true);
    try {
      const response = await resumeAPI.predictNextSkills({
        itSkills: resumeData.it_skills,
        softSkills: resumeData.soft_skills,
        designation: targetDesignation,
      });
      const formattedSkills = response.data.predicted_next_it_skills.map(skill =>
        skill.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
      );
      setRecommendations({
        title: formattedSkills[0],
        skills: formattedSkills,
        impact: 'High',
      });
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-5">
      <div className="mb-5">
        <h3 className="text-lg font-semibold text-gray-900">Next Best Step</h3>
        <p className="text-xs text-gray-400 mt-0.5">Skill recommendations</p>
      </div>

      {!recommendations ? (
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-50 mb-4">
            <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500 mb-5 max-w-xs mx-auto">
            Get personalized recommendations based on your profile and target role
          </p>
          <button onClick={generateRecommendations} disabled={loading} className="btn-primary">
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                Analyzing...
              </span>
            ) : 'Generate Recommendations'}
          </button>
        </div>
      ) : (
        <div className="space-y-4 animate-fade-in-up">
          <div className="flex items-start justify-between">
            <h4 className="font-semibold text-gray-900">{recommendations.title}</h4>
            <span className="tag tag-amber text-xs">{recommendations.impact} Impact</span>
          </div>

          <div>
            <p className="text-xs font-medium text-gray-500 mb-2">Recommended Skills</p>
            <div className="flex flex-wrap gap-1.5">
              {recommendations.skills.map((skill, index) => (
                <span
                  key={index}
                  className="tag tag-indigo animate-fade-in"
                  style={{ animationDelay: `${index * 60}ms`, animationFillMode: 'both' }}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          <button onClick={generateRecommendations} disabled={loading} className="btn-secondary text-sm w-full">
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                Regenerating...
              </span>
            ) : 'Regenerate'}
          </button>
        </div>
      )}
    </div>
  );
};

export default NextBestStep;
