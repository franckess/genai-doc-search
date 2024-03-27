import React, { useState, useEffect, KeyboardEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { API } from "aws-amplify";
import { Conversation, ConversationDetail } from "../common/types";
import ChatSidebar from "../components/ChatSidebar";
import ChatMessages from "../components/ChatMessages";
import LoadingGrid from "../../public/loading-grid.svg";

const Document: React.FC = () => {
  const params = useParams();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<Conversation[] | undefined>(undefined);
  const [conversation, setConversation] = useState<ConversationDetail | undefined>(undefined);
  const [loading, setLoading] = React.useState<string>("idle");
  const [messageStatus, setMessageStatus] = useState<string>("idle");
  const [conversationListStatus, setConversationListStatus] = useState("idle");
  const [prompt, setPrompt] = useState("");

  const selectedConversationId = params.conversationid || conversations?.[0]?.conversationid;

  const fetchConversations = async () => {
    setLoading("loading");
    const conversations = await API.get("serverless-pdf-chat", "conversations", {});
    setConversations(conversations);
    setLoading("idle");
  };

  const fetchConversation = async (conversationid: string) => {
    const response = await API.get("serverless-pdf-chat", `conversations/${conversationid}`, {});
    setConversation(response.conversation);
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selectedConversationId) {
      fetchConversation(selectedConversationId);
    }
  }, [selectedConversationId])


  const handlePromptChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPrompt(event.target.value);
  };

  const addConversation = async () => {
    setConversationListStatus("loading");
    const newConversation = await API.post("serverless-pdf-chat", "conversations", {});
    await fetchConversations();
    navigate(`/conversations/${newConversation.conversationid}`);
    setConversationListStatus("idle");
  };

  const switchConversation = (conversationid: string) => {
    navigate(`/conversations/${conversationid}`);
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key == "Enter") {
      submitMessage();
    }
  };

  const submitMessage = async () => {    
    if (conversation) {
      setMessageStatus("loading");

      const previewMessage = {
        type: "text",
        data: {
          content: prompt,
          example: false,
        },
      };

      console.log('preview message');

      const updatedConversation = {
        ...conversation,
        messages: [...(conversation.messages || []), previewMessage],
      };

      setConversation(updatedConversation);

      await API.post(
        "serverless-pdf-chat",
        `conversations/${conversation.conversationid}`,
        { body: { prompt: prompt } }
      );
      setPrompt("");
      await fetchConversation(conversation.conversationid);
      setMessageStatus("idle");
    }
  };

  return (
    <div className="">
      {loading === "loading" && !conversations && (
        <div className="flex flex-col items-center mt-6">
          <img src={LoadingGrid} width={40} />
        </div>
      )}
      {conversations && (
        <div className="grid grid-cols-12 border border-gray-200 rounded-lg">
          <ChatSidebar
            conversations={conversations}
            selectedConversationId={selectedConversationId}
            addConversation={addConversation}
            switchConversation={switchConversation}
            conversationListStatus={conversationListStatus}
          />
          {conversation && (
            <ChatMessages
              prompt={prompt}
              conversation={conversation}
              messageStatus={messageStatus}
              submitMessage={submitMessage}
              handleKeyPress={handleKeyPress}
              handlePromptChange={handlePromptChange}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default Document;
