import { Document } from "../common/types";
import { getDateTime } from "../common/utilities";
import { filesize } from "filesize";
import {
  DocumentIcon,
  CircleStackIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";

const DocumentDetail: React.FC<Document> = (document: Document) => {
  return (
    <>
      <h3 className="text-center mb-3 text-lg font-bold tracking-tight text-gray-900">
        {document.filename}
      </h3>
      <div className="flex flex-col space-y-2">
        <div className="inline-flex items-center">
          <DocumentIcon className="w-4 h-4 mr-2" />
          {document.pages} pages
        </div>
        <div className="inline-flex items-center">
          <CircleStackIcon className="w-4 h-4 mr-2" />
          {filesize(Number(document.filesize)).toString()}
        </div>
        <div className="inline-flex items-center">
          <ClockIcon className="w-4 h-4 mr-2" />
          {getDateTime(document.created)}
        </div>
      </div>
    </>
  );
};

export default DocumentDetail;
