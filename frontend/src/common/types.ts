export interface Document {
  documentid: string;
  userid: string;
  filename: string;
  filesize: string;
  created: string;
  pages: string;
}

export interface Conversation {
  userid: string;
  conversationid: string;
  created: string;
}

export interface ConversationDetail {
  userid: string;
  conversationid: string;
  created: string;
  messages: {
    type: string;
    data: {
      content: string;
      example: boolean;
    };
  }[];
}
