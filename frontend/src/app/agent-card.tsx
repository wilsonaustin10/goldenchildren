'use client';
import Image from 'next/image';
import Link from 'next/link';

export type P = {
    name: string;
    description: string;
    image: unknown;
    href: string;
}

export default function AgentCard({name, description, image, href}: P) {
  return (
    <Link href={href}>
        <div className='flex flex-col gap-y-2 cursor-pointer transition hover:bg-neutral-600 p-4'>
            <Image src={image} alt={name} width={150} height={150} />
            <div className='text-xl text-white font-bold'>{name}</div>
            <div className='text-neutral-300'>{description}</div>
        </div>
    </Link>
  )
}
