'use client';

import { useChatbot } from '@/hooks/useChatbot';
import React from 'react';

interface BrowserUseFunction {
  name: string;
  args: Record<string, any>;
  description?: string | null;
}

interface BrowserUsePlanProps {
  plan: {
    functions: BrowserUseFunction[];
    explanation?: string | null;
    action_description?: string | null;
  };
}

const BrowserUsePlan: React.FC<BrowserUsePlanProps> = ({ plan }) => {
  if (!plan || !plan.functions || plan.functions.length === 0) {
    return <div className="text-gray-400">No BrowserUse plan available</div>;
  }

  const {sendMessage} = useChatbot();

  return (
    <div className="bg-neutral-900 rounded-lg p-4 text-white">
      <h2 className="text-xl font-bold mb-4">BrowserUse Plan</h2>
      
      {plan.action_description && (
        <div className="mb-4 p-3 bg-neutral-800 rounded border border-neutral-700">
          <h3 className="text-lg font-semibold mb-2">Original Request</h3>
          <p className="text-gray-300">{plan.action_description}</p>
        </div>
      )}
      
      {plan.explanation && (
        <div className="mb-4 p-3 bg-neutral-800 rounded border border-neutral-700">
          <h3 className="text-lg font-semibold mb-2">Explanation</h3>
          <p className="text-gray-300">{plan.explanation}</p>
        </div>
      )}
      
      <h3 className="text-lg font-semibold mb-2">Function Calls</h3>
      <div className="space-y-3">
        {plan.functions.map((func, index) => (
          <div key={index} className="p-3 bg-neutral-800 rounded border border-neutral-700">
            <div className="flex items-center mb-2">
              <span className="text-blue-400 font-mono">{func.name}</span>
              <span className="text-gray-400 text-sm ml-2">({Object.keys(func.args).join(', ')})</span>
            </div>
            
            <div className="pl-4 border-l-2 border-blue-800">
              {Object.entries(func.args).map(([key, value]) => (
                <div key={key} className="flex mb-1">
                  <span className="text-gray-400 font-mono w-24">{key}:</span>
                  <span className="text-green-400 font-mono overflow-hidden text-ellipsis">
                    {typeof value === 'string' 
                      ? `"${value}"` 
                      : JSON.stringify(value)}
                  </span>
                </div>
              ))}
            </div>
            
            {func.description && (
              <div className="mt-2 text-sm text-gray-400">
                {func.description}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-4 flex justify-end">
        <button 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white"
          onClick={() => {
            // This is where you would execute the BrowserUse plan
            console.log('Executing BrowserUse plan:', plan);
            if(confirm('This would execute the BrowserUse plan in a real implementation')) {
              sendMessage(`To find the profiles of oscar nominated best supporting actors, you must use google to get names of nominated actors, and search their name on IMDB. Then, copy the URL of the actor page and return it.
`, "browser-use")
            }
            
          }}
        >
          Execute Plan
        </button>
      </div>
    </div>
  );
};

export default BrowserUsePlan; 