I don't believe in duplicating effort, here are the projects I'm stealing from

NBT
===

We use a slightly modified version of Thomas Woolford's NBT parser in spock/mcp/nbt.py, original can be found here: https://github.com/twoolie/NBT

Copyright (c) 2010 Thomas Woolford

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.


BarneyMC
========

We use slightly modified versions of large parts of Barney Gale's implementation of the MC Protocol, which can be found here: https://github.com/barneygale/barneymc

Large parts of spock/mcp/mcpacket.py, spock/mcp/mcdata.py, and spock/mcp/mcpacket_extensions.py are verbatim copies of his work simply updated to work with the current protocol

pyCraft
=======

Large parts of Spock's design were inspired by Ammar Askar's pyCraft, which can be found here: https://github.com/ammaraskar/pyCraft

We use his implementation of the Minecraft.net login, found in spock/utils.py

Copyright 2012 Ammar Askar

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.