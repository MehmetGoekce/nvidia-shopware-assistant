/*
 * SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";

const Footer: React.FC = () => {
  return (
    <div className="bg-[#F2F2F2] w-[100%] absolute bottom-0 right-0 h-[64px] mt-4 font-bold text-[28px] flex items-center justify-center">
      <div className="bg-[#F2F2F2] mt-[1px] text-white lg:px-8 flex items-center gap-6">
        <div className="flex items-center gap-1">
          <p className="text-[13px] text-[#999] font-normal">
            Powered by MEMOTECH &times; NVIDIA AI Blueprints
          </p>
        </div>
        <div className="flex items-center gap-1 hover:underline">
          <p className="text-[15px] text-[#666] font-medium hover:underline">KONTAKT</p>
        </div>
        <div className="flex items-center gap-1 hover:underline">
          <p className="text-[15px] text-[#666] font-medium hover:underline">DATENSCHUTZ</p>
        </div>
      </div>
    </div>
  );
};

export default Footer;
