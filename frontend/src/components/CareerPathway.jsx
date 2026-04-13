import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { resumeAPI } from '../config/api-resume-processor';
import { setPresenting, setIdle } from '../store/avatarSlice';

const CareerPathway = ({ resumeData, targetDesignation }) => {
  const dispatch = useDispatch();
  const [pathway, setPathway] = useState(null);
  const [loading, setLoading] = useState(false);

  // Clear pathway when target designation changes
  useEffect(() => {
    setPathway(null);
  }, [targetDesignation]);

  const generatePathway = async () => {
    setLoading(true);
    dispatch(setPresenting('Building career roadmap...'));
    try {
      // Use the old /predict API to get meaningful recommendations
      const response = await resumeAPI.predictNextSkills({
        itSkills: resumeData?.it_skills || [],
        softSkills: resumeData?.soft_skills || [],
        designation: targetDesignation || "",
      });

      const itSkills = response.data.predicted_next_it_skills || [];
      const softSkills = response.data.predicted_next_soft_skills || [];
      
      // Transform predictions into career pathway stages
      const allSkills = [...itSkills, ...softSkills];
      const currentLevel = resumeData?.designition?.[0] || "Entry Level";
      const targetRole = targetDesignation || "Senior Role";
      
      // Create meaningful stages based on skill predictions
      const stages = [];
      
      // Foundation stage (first 1/3 of skills)
      const foundationSkills = allSkills.slice(0, Math.ceil(allSkills.length / 3));
      if (foundationSkills.length > 0) {
        stages.push({
          title: "Foundation Building",
          duration: "3-6 months",
          skills: foundationSkills.map(skill => 
            skill.split('_').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
          ),
          milestones: [
            `Master ${foundationSkills[0]?.replace(/_/g, ' ')}`,
            "Build practical projects",
            "Complete relevant certification"
          ],
          status: "current"
        });
      }
      
      // Advanced stage (middle 1/3 of skills)
      const advancedSkills = allSkills.slice(Math.ceil(allSkills.length / 3), Math.ceil(2 * allSkills.length / 3));
      if (advancedSkills.length > 0) {
        stages.push({
          title: "Advanced Development",
          duration: "6-12 months",
          skills: advancedSkills.map(skill => 
            skill.split('_').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
          ),
          milestones: [
            "Lead complex projects",
            "Mentor junior colleagues",
            "Contribute to system architecture"
          ],
          status: "upcoming"
        });
      }
      
      // Specialization stage (last 1/3 of skills)
      const expertSkills = allSkills.slice(Math.ceil(2 * allSkills.length / 3));
      if (expertSkills.length > 0) {
        stages.push({
          title: "Specialization & Leadership",
          duration: "12-18 months",
          skills: expertSkills.map(skill => 
            skill.split('_').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
          ),
          milestones: [
            "Become domain expert",
            "Drive technical strategy",
            "Lead cross-functional teams"
          ],
          status: "future"
        });
      }
      
      // Fallback if no predictions available
      if (stages.length === 0) {
        stages.push({
          title: "Skill Development",
          duration: "6-12 months",
          skills: ["Continuous Learning", "Professional Development"],
          milestones: ["Identify growth opportunities", "Build relevant skills"],
          status: "current"
        });
      }

      setPathway({
        currentLevel,
        targetRole,
        stages,
        timelineTotal: stages.length > 2 ? "2-3 years" : stages.length > 1 ? "1-2 years" : "6-12 months"
      });
      dispatch(setPresenting('Career roadmap ready!'));
      setTimeout(() => dispatch(setIdle()), 2000);
    } catch (error) {
      console.error('Failed to generate pathway:', error);
      // Fallback pathway on error
      setPathway({
        currentLevel: resumeData?.designition?.[0] || "Current Role",
        targetRole: targetDesignation || "Target Role",
        stages: [
          {
            title: "Skill Assessment",
            duration: "1-2 months",
            skills: ["Self Assessment", "Goal Setting"],
            milestones: ["Complete skills audit", "Define career goals"],
            status: "current"
          },
          {
            title: "Professional Development",
            duration: "6-12 months",
            skills: ["Industry Knowledge", "Technical Skills"],
            milestones: ["Complete relevant training", "Build portfolio"],
            status: "upcoming"
          }
        ],
        timelineTotal: "1-2 years"
      });
      dispatch(setIdle());
    } finally {
      setLoading(false);
    }
  };

  const statusStyles = {
    current: { dot: 'bg-emerald-500', line: 'border-emerald-200', bg: 'bg-emerald-50' },
    upcoming: { dot: 'bg-amber-400', line: 'border-amber-200', bg: 'bg-amber-50' },
    future: { dot: 'bg-gray-300', line: 'border-gray-200', bg: 'bg-gray-50' },
  };

  return (
    <div className="card p-5">
      <div className="mb-5">
        <h3 className="text-lg font-semibold text-gray-900">Career Pathway</h3>
        <p className="text-xs text-gray-400 mt-0.5">Your personalized career roadmap</p>
      </div>

      {!pathway ? (
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-violet-50 mb-4">
            <svg className="w-6 h-6 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <p className="text-sm text-gray-500 mb-5 max-w-xs mx-auto">
            Generate a step-by-step career roadmap based on your skills and goals
          </p>
          <button onClick={generatePathway} disabled={loading} className="btn-primary">
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                Generating...
              </span>
            ) : 'Generate Roadmap'}
          </button>
        </div>
      ) : (
        <div className="space-y-5 animate-fade-in-up">
          {/* Progress header */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
            <div className="flex-1 min-w-0">
              <p className="text-xs text-gray-400">Current</p>
              <p className="text-sm font-medium text-gray-900 truncate">{pathway.currentLevel}</p>
            </div>
            <svg className="w-4 h-4 text-gray-300 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            <div className="flex-1 min-w-0 text-right">
              <p className="text-xs text-gray-400">Target</p>
              <p className="text-sm font-medium text-gray-900 truncate">{pathway.targetRole}</p>
            </div>
          </div>

          {/* Timeline */}
          <div className="space-y-0">
            {pathway.stages.map((stage, index) => {
              const style = statusStyles[stage.status];
              return (
                <div
                  key={index}
                  className="relative pl-7 pb-6 last:pb-0 animate-fade-in-up"
                  style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}
                >
                  {/* Timeline line */}
                  {index < pathway.stages.length - 1 && (
                    <div className={`absolute left-[9px] top-5 bottom-0 w-px border-l-2 border-dashed ${style.line}`} />
                  )}
                  {/* Timeline dot */}
                  <div className={`absolute left-0 top-1 w-[18px] h-[18px] rounded-full border-[3px] border-white ${style.dot} shadow-sm`} />

                  <div className={`${style.bg} rounded-xl p-4`}>
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="text-sm font-semibold text-gray-900">{stage.title}</h4>
                      <span className="text-xs text-gray-400 flex-shrink-0 ml-2">{stage.duration}</span>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <p className="text-xs font-medium text-gray-400 mb-1.5">Skills</p>
                        <div className="flex flex-wrap gap-1">
                          {stage.skills.map((skill, i) => (
                            <span key={i} className="tag tag-indigo text-[11px]">{skill}</span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-400 mb-1.5">Milestones</p>
                        <ul className="space-y-1">
                          {stage.milestones.map((milestone, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
                              <span className={`w-1 h-1 rounded-full mt-1.5 flex-shrink-0 ${style.dot}`}></span>
                              {milestone}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-xs text-gray-400">Est. timeline: {pathway.timelineTotal}</span>
            <button onClick={generatePathway} disabled={loading} className="btn-secondary text-sm py-1.5 px-3">
              {loading ? 'Generating...' : 'Regenerate'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerPathway;
