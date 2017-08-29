        var oInputField;    
        var oPopDiv;  
        var oItem_ul;  
        //var aItems = ['102','103','104','105','107','106','108','109','110','202','203','204','205','206','207','208','209','210','312','314','316','318','320','322','324','326','328','330','335','340','322','324','326','328','330','335','340','404','405','406','407','408','409','410','411','412','413','414'];  
        aItems.sort();  //按字母排序  
        function initVars(){  
            //初始化变量  
            oInputField = document.forms["item_form"].member_phone;  
            oPopDiv = document.getElementById("popup");  
            oItem_ul = document.getElementById("item_ul");  
        }  
        function findItems(){  
            initVars();  //初始化变量  
            if(oInputField.value.length > 0){  
                var aResult = new Array();  //用于存放匹配结果  
                for(var i = 0 ; i < aItems.length ; i++ ){  
                    //必须是从单词的开始处匹配  
                    if(aItems[i].indexOf(oInputField.value) == 0)  
                        aResult.push(aItems[i]); //加入结果  
                }  
                if(aResult.length > 0)  //如果有匹配的item则显示出来  
                    setItems(aResult);  
                else                        //否则就清除、用户多输入一个字母  
                    clearItems();  //就有可能从有匹配到无、到无的时候需要清除  
            }  
            else  
                clearItems(); //无输入时清除提示框  
        }  
          
          
        function clearItems(){  
            //清除提示内容  
            for(var i = oItem_ul.childNodes.length - 1 ; i >= 0 ; i-- )  
                oItem_ul.removeChild(oItem_ul.childNodes[i]);  
            oPopDiv.className = "hidden";  
        }  
          
        function setItems(the_Items){  
            //显示提示框、传入的参数即为匹配出来的结果组成的数组  
            clearItems();  //没输入一个字母就先清楚原先的提示、再继续  
            oPopDiv.className = "show" ;  
            var oLi ;  
            for(var i = 0 ; i < the_Items.length ; i++ ){  
                //将匹配的提示结果逐一显示给用户  
                oLi = document.createElement("li");  
                oItem_ul.appendChild(oLi);  
                oLi.appendChild(document.createTextNode(the_Items[i]));  
                  
                oLi.onmouseover = function(){  
                    this.className = "success" ;  //鼠标指针经过时高亮  
                }  
                oLi.onmouseout = function(){  
                    this.className = "" ;   //鼠标指针离开时恢复原样  
                } 
                oLi.onclick = function(){  
                    //用户单击某个匹配项时、设置输入框为该项的值  
                    oInputField.value = this.firstChild.nodeValue;  
                    clearItems();  //同时清除提示框  
                }  
            }  
        } 