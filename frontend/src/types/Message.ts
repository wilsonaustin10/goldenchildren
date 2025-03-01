
export enum Sender {
    USER = 'user',
    AI = 'ai'
}
export type Message = {
    text: string;
    sender: Sender;
    needsMoreInfo?: boolean
};
