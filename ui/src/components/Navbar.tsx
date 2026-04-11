/*
 * SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Navigation bar component
 */

import React from "react";
import MenuIcon from "@mui/icons-material/Menu";
import { config } from "../config/config";
import { NavbarProps } from "../types";

const Navbar: React.FC<NavbarProps> = ({ onCategoryClick }) => {
  const { categories, categoryPrompts } = config.ui;

  return (
    <div>
      {/* Main navigation bar */}
      <div className="bg-[#FFFFFF] h-[48px] px-3 py-2 lg:px-5 text-white flex justify-between items-center">
        {/* Left side - Menu and Brand */}
        <div className="flex items-center shrink-0">
          <MenuIcon sx={{ color: "#5E5E5E" }} fontSize="small" />
          <p className="text-[22px] ml-[20px] font-bold text-[#202020]">
            MEMOTECH
          </p>
        </div>

        {/* Right side - Welcome message */}
        <div className="flex items-center gap-x-2">
          <div className="flex items-center gap-2 p-3 rounded-full">
            <p className="text-[14px] text-[#202020]">Willkommen!</p>
          </div>
        </div>
      </div>

      {/* Categories bar */}
      <div className="bg-[#F2F2F2] mt-[1px] h-[57px] text-white px-3 py-2 lg:px-8 flex items-center gap-8">
        {(Object.keys(categories) as Array<keyof typeof categories>).map((key) => (
          <button
            key={key}
            onClick={() => onCategoryClick(categoryPrompts[key])}
            className={`flex items-center text-[15px] font-medium hover:underline cursor-pointer bg-transparent border-none p-0 ${
              key === 'fashion' ? 'text-[#000] underline' : 'text-[#666]'
            }`}
          >
            {categories[key]}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Navbar;
