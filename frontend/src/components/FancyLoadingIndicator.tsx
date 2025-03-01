import styles from './FancyLoadingIndicator.module.css';

export const FancyLoadingIndicator = () => {
    return (
        <div className={styles.loadingContainer}>
            <div className={styles.brainPulse}>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3Z" className={styles.brain}/>
                    <path d="M12 8C9.79086 8 8 9.79086 8 12C8 14.2091 9.79086 16 12 16C14.2091 16 16 14.2091 16 12C16 9.79086 14.2091 8 12 8Z" className={styles.core}/>
                </svg>
            </div>
            <div className={styles.pulseText}>Processing</div>
        </div>
    );
};