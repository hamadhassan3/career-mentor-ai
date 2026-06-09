import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { resumeAPI } from '../config/api-resume-processor';
import { resumeAPI as backendResumeAPI } from '../config/api-backend';
import { setPresenting, setIdle } from '../store/avatarSlice';
import { formatSkill } from '../utils/skills';

// Horizontal gutters (as % of width) the trail weaves between
const LEFT = 15;
const RIGHT = 85;
const nodeX = (index) => (index % 2 === 0 ? LEFT : RIGHT);

const FlagIcon = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 21V4" />
    <path strokeLinejoin="round" d="M5 4h10l-2 3 2 3H5z" fill="currentColor" />
  </svg>
);

const TargetIcon = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="8" />
    <circle cx="12" cy="12" r="4" />
    <circle cx="12" cy="12" r="1.25" fill="currentColor" stroke="none" />
  </svg>
);

// A soft curve sweeping from one gutter to another (the path between stops)
const TrailConnector = ({ fromX, toX }) => (
  <div className="h-9 text-gray-300">
    <svg className="w-full h-full" viewBox="0 0 100 36" preserveAspectRatio="none" fill="none">
      <path
        d={`M ${fromX} 0 C ${fromX} 18, ${toX} 18, ${toX} 36`}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  </div>
);

const CareerPathway = ({ resumeData, targetDesignation }) => {
  const dispatch = useDispatch();
  const [pathway, setPathway] = useState(null);
  const [loading, setLoading] = useState(false);

  // Clear pathway when target designation changes
  useEffect(() => {
    setPathway(null);
  }, [targetDesignation]);

  // Load existing career pathway when component mounts
  useEffect(() => {
    const loadExistingPathway = async () => {
      try {
        const response = await backendResumeAPI.getCareerPathway();
        const pathwayData = response.data;

        // Transform backend data to match frontend format
        setPathway({
          currentLevel: pathwayData.current_level,
          targetRole: pathwayData.target_role,
          stages: pathwayData.stages || [],
        });
      } catch (error) {
        // No existing pathway found, which is fine
        if (error.response?.status !== 404) {
          console.error('Failed to load existing career pathway:', error);
        }
      }
    };

    if (resumeData && targetDesignation) {
      loadExistingPathway();
    }
  }, [resumeData, targetDesignation]);

  const generatePathway = async () => {
    setLoading(true);
    dispatch(setPresenting('Fawkes is building your career roadmap...'));
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
          skills: foundationSkills.map(formatSkill),
          status: "current"
        });
      }

      // Advanced stage (middle 1/3 of skills)
      const advancedSkills = allSkills.slice(Math.ceil(allSkills.length / 3), Math.ceil(2 * allSkills.length / 3));
      if (advancedSkills.length > 0) {
        stages.push({
          title: "Advanced Development",
          skills: advancedSkills.map(formatSkill),
          status: "upcoming"
        });
      }

      // Specialization stage (last 1/3 of skills)
      const expertSkills = allSkills.slice(Math.ceil(2 * allSkills.length / 3));
      if (expertSkills.length > 0) {
        stages.push({
          title: "Specialization & Leadership",
          skills: expertSkills.map(formatSkill),
          status: "future"
        });
      }

      // Fallback if no predictions available
      if (stages.length === 0) {
        stages.push({
          title: "Skill Development",
          skills: ["Continuous Learning", "Professional Development"],
          status: "current"
        });
      }

      const pathwayData = {
        currentLevel,
        targetRole,
        stages,
      };

      setPathway(pathwayData);

      // Save to database
      try {
        await backendResumeAPI.saveCareerPathway({
          current_level: currentLevel,
          target_role: targetRole,
          target_designation: targetDesignation,
          stages: stages,
        });
      } catch (error) {
        console.error('Failed to save career pathway to database:', error);
      }

      dispatch(setPresenting('Fawkes has your career roadmap ready!'));
      setTimeout(() => dispatch(setIdle()), 2000);
    } catch (error) {
      console.error('Failed to generate pathway:', error);
      // Fallback pathway on error
      const fallbackPathway = {
        currentLevel: resumeData?.designition?.[0] || "Current Role",
        targetRole: targetDesignation || "Target Role",
        stages: [
          {
            title: "Skill Assessment",
            skills: ["Self Assessment", "Goal Setting"],
            status: "current"
          },
          {
            title: "Professional Development",
            skills: ["Industry Knowledge", "Technical Skills"],
            status: "upcoming"
          }
        ],
      };

      setPathway(fallbackPathway);

      // Save fallback to database
      try {
        await backendResumeAPI.saveCareerPathway({
          current_level: fallbackPathway.currentLevel,
          target_role: fallbackPathway.targetRole,
          target_designation: targetDesignation,
          stages: fallbackPathway.stages,
        });
      } catch (dbError) {
        console.error('Failed to save fallback career pathway to database:', dbError);
      }

      dispatch(setIdle());
    } finally {
      setLoading(false);
    }
  };

  const stages = pathway?.stages || [];

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
        <div className="animate-fade-in-up">
          {/* Start — current level */}
          <div className="flex justify-center">
            <div className="inline-flex items-center gap-2 max-w-full pl-2 pr-3.5 py-1.5 rounded-full bg-white border border-gray-200">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-emerald-50 flex-shrink-0">
                <FlagIcon className="w-3.5 h-3.5 text-emerald-500" />
              </span>
              <div className="text-left leading-tight min-w-0">
                <p className="text-xs uppercase tracking-wider text-gray-400">Now</p>
                <p className="text-sm font-semibold text-gray-900 break-words">{pathway.currentLevel}</p>
              </div>
            </div>
          </div>

          {/* The weaving trail of steps */}
          {stages.map((stage, i) => {
            const x = nodeX(i);
            const fromX = i === 0 ? 50 : nodeX(i - 1);
            const isLeft = x === LEFT;
            const isCurrent = stage.status === 'current';
            return (
              <React.Fragment key={i}>
                <TrailConnector fromX={fromX} toX={x} />
                <div className={`relative ${isLeft ? 'pl-[30%] pr-1' : 'pr-[30%] pl-1 text-right'}`}>
                  {/* vertical rail beside the step */}
                  <div className="absolute top-8 bottom-0 w-0.5 -translate-x-1/2 bg-gray-300" style={{ left: `${x}%` }} />

                  {/* numbered step */}
                  <div
                    className={`absolute top-0 z-10 -translate-x-1/2 flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold ${
                      isCurrent
                        ? 'bg-violet-600 text-white'
                        : 'bg-violet-50 text-violet-600 border border-violet-200'
                    }`}
                    style={{ left: `${x}%` }}
                  >
                    {i + 1}
                  </div>

                  {/* step content */}
                  <div className="relative z-10 min-h-[2.5rem]">
                    <h4 className="text-sm font-semibold text-gray-900">{stage.title}</h4>
                    {stage.skills?.length > 0 && (
                      <div className={`flex flex-wrap gap-1 mt-1.5 ${isLeft ? '' : 'justify-end'}`}>
                        {stage.skills.map((skill, j) => (
                          <span key={j} className="text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded-full">{skill}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </React.Fragment>
            );
          })}

          {/* Trail into the goal */}
          <TrailConnector fromX={stages.length === 0 ? 50 : nodeX(stages.length - 1)} toX={50} />

          {/* Goal — target role */}
          <div className="flex justify-center">
            <div className="inline-flex items-center gap-2 max-w-full pl-2 pr-4 py-2 rounded-full bg-violet-600 text-white">
              <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-white bg-opacity-20 flex-shrink-0">
                <TargetIcon className="w-4 h-4 text-white" />
              </span>
              <div className="text-left leading-tight min-w-0">
                <p className="text-xs uppercase tracking-wider text-violet-200">Goal</p>
                <p className="text-sm font-bold break-words">{pathway.targetRole}</p>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end pt-4">
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
