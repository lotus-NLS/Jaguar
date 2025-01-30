// import React from "react";
//
// const ChatPage = () => {
//     const messages = [
//         {id: 1, text: "Hello! How can I help you today?", sender: "bot"},
//         {id: 2, text: "I need some information on your services.", sender: "user"},
//         {id: 3, text: "Sure! We offer a range of solutions including...", sender: "bot"},
//     ];
//
//
//     const page = (
//         <div className="flex flex-col items-center justify-center min-h-screen p-4">
//             <div className="w-full max-w-md p-4 bg-white shadow-lg rounded-2xl">
//                 <h2 className="text-xl font-bold mb-4">Chat</h2>
//                 <div className="space-y-2">
//                     {messages.map((msg) => (
//                         <div
//                             key={msg.id}
//                             className={`p-2 rounded-lg w-fit max-w-xs ${
//                                 msg.sender === "user" ? "bg-blue-500 text-white ml-auto" : "bg-gray-200"
//                             }`}
//                         >
//                             {msg.text}
//                         </div>
//                     ))}
//                 </div>
//             </div>
//         </div>
//     );
//
//
//     return page;
// }
//
//
// export default ChatPage;


import React from "react";

const ChatPage = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-32 h-32 bg-red-500 rounded-2xl"></div>
    </div>
  );
};

export default ChatPage;