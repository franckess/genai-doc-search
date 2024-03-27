import { Link } from "react-router-dom";
import { Menu } from "@headlessui/react";
import {
  ArrowLeftOnRectangleIcon,
  ChevronDownIcon,
  DocumentArrowUpIcon,
} from "@heroicons/react/24/outline";
import { ChatBubbleLeftRightIcon } from "@heroicons/react/24/solid";

interface NavigationProps {
  userInfo: any;
  handleSignOutClick: (
    event: React.MouseEvent<HTMLButtonElement>
  ) => Promise<void>;
}

const Navigation: React.FC<NavigationProps> = ({
  userInfo,
  handleSignOutClick
}: NavigationProps) => {
  return (
    <nav className="border-cevo border-b-2">
      <div className="container flex flex-wrap items-center justify-between py-3 ">
        <div className="flex gap-10">
          <img src="/CEVO-logo.png" className="w-28 h-8"/>
            <Link
              to="/"
              className="inline-flex items-center self-center text-xl font-semibold whitespace-nowrap"
            >
              <ChatBubbleLeftRightIcon className="w-6 h-6 mr-1.5" />
              Chat
            </Link>
            <Link
              to="/documents"
              className="inline-flex items-center self-center text-xl font-semibold whitespace-nowrap"
            >
              <DocumentArrowUpIcon className="w-6 h-6 mr-1.5" />
              Documents
            </Link>
          
        </div>
        
        <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
          <div className="relative ml-3">
            <Menu>
              <Menu.Button className="text-center inline-flex items-center text-sm underline-offset-2 hover:underline">
                {userInfo?.attributes?.email}
                <ChevronDownIcon className="w-3 h-3 ml-1" />
              </Menu.Button>
              <Menu.Items className="absolute right-0 z-10 mt-2 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div className="px-1 py-1 ">
                  <Menu.Item>
                    <button
                      onClick={handleSignOutClick}
                      className="group w-full inline-flex items-center rounded-md px-2 py-2 text-sm underline-offset-2 hover:underline"
                    >
                      <ArrowLeftOnRectangleIcon className="w-4 h-4 mr-1" />
                      Sign Out
                    </button>
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Menu>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
