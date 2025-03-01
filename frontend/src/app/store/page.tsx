import React from 'react'
import AgentCard from '../agent-card'
import sage from '../../public/icons/sage.png';
import checkbox from '../../public/icons/checkbox.png';
import scout from '../../public/icons/scout.png';
import buddy from '../../public/icons/buddy.png';

export default function Store() {
  return (
    <div className=' bg-neutral-900 min-h-screen px-8 pb-16'>
        <div className='flex flex-col py-16'>
            <h1 className='text-5xl text-center font-bold text-white'>Golden Children - Store</h1>
            <h3 className='text-lg text-gray-500 text-center'>In this section you will find a high level overview of all the agents available on Golden Children</h3>
        </div>
        <section className=''>
            <h2 className='text-2xl font-bold text-white mb-4'>Agents</h2>
            <div className='grid grid-cols-2 gap-4'>
                <div className='col-span-1 '>
                    <div className='p-4 h-full'>
                        <AgentCard name="SageGPT" 
                            description="A knowledge-driven AI that provides expert-level answers, research summaries, and fact-checked insights for professionals, students, and curious minds." 
                            image={sage}
                            href={"/chat"}
                            />
                    </div>
                </div>
                <div className='col-span-1'>
                    <div className='p-4 h-full'>
                    <AgentCard name="ShopScout" 
                            description="A shopping assistant that finds the best deals, compares product reviews, and recommends purchases based on user preferences and budget." 
                            image={scout}
                            href={"/chat"}
                            />
                    </div>
                </div>
                <div className='col-span-1'>
                    <div className='p-4 h-full'>
                    <AgentCard name="TaskMate" 
                            description="A productivity assistant that helps users manage schedules, automate repetitive tasks, and optimize workflow efficiency through smart reminders and integrations." 
                            image={checkbox}
                            href={"/chat"}
                            />
                    </div>
                </div>
                <div className='col-span-1'>
                    <div className='p-4 h-full'>
                    <AgentCard name="ChatBuddy" 
                        description="A conversational AI that engages in casual discussions, provides emotional support, and offers personalized entertainment recommendations." 
                        image={buddy}
                        href={"/chat"}
                        />
                    </div>
                </div>
            </div>
        </section>
    </div>
  )
}
