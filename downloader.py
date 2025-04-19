import requests
from bs4 import BeautifulSoup
import json
import os

def download_papers(scientist, year, output_file):
    """
    下载指定科学家在给定年份的论文，并保存到 JSON 文件中。

    参数:
      scientist: 科学家姓名，用于在 dblp 搜索。
      year: 年份过滤条件，只有年份匹配的论文会被保存。
      output_file: 保存输出 JSON 文件的路径及文件名。
    """
    search_url = "https://dblp.org/search?q=" + requests.utils.quote(scientist)
    print(f"搜索 URL: {search_url}")

    # 获取搜索结果
    search_resp = requests.get(search_url)
    search_soup = BeautifulSoup(search_resp.content, "html.parser")
    profile_link_tag = search_soup.find("a", href=lambda href: href and "/pid/" in href)

    result = []
    profile_url = ""
    if profile_link_tag:
        profile_url = profile_link_tag["href"]
        if not profile_url.startswith("http"):
            profile_url = "https://dblp.org" + profile_url
        
        # 获取个人主页内容
        profile_resp = requests.get(profile_url)
        profile_soup = BeautifulSoup(profile_resp.content, "html.parser")
        
        # 查找所有论文条目
        papers = profile_soup.find_all("cite", class_="data tts-content")
    
        for paper in papers:
            paper_info = {}
            
            # 提取作者列表
            authors = []
            for author_span in paper.find_all("span", itemprop="author"):
                name_span = author_span.find("span", itemprop="name")
                if name_span:
                    authors.append(name_span.get_text(strip=True))
            paper_info["authors"] = authors
            
            # 提取论文标题
            title_span = paper.find("span", class_="title")
            paper_info["title"] = title_span.get_text(strip=True) if title_span else ""
            
            # 提取会议信息
            venue_info = {}
            venue_tag = paper.find("span", itemprop="isPartOf", itemtype="http://schema.org/Periodical")
            if venue_tag:
                name_tag = venue_tag.find("span", itemprop="name")
                if name_tag:
                    venue_info["name"] = name_tag.get_text(strip=True)
                volume_tag = paper.find("span", itemprop="isPartOf", itemtype="http://schema.org/PublicationVolume")
                if volume_tag:
                    vol_span = volume_tag.find("span", itemprop="volumeNumber")
                    if vol_span:
                        venue_info["volume"] = vol_span.get_text(strip=True)
            paper_info["venue"] = venue_info
            
            # 提取arXiv链接
            arxiv_link = ""
            publ_nav = paper.find_next("nav", class_="publ")
            if publ_nav:
                head_div = publ_nav.find("div", class_="head")
                if head_div:
                    arxiv_tag = head_div.find("a", href=True)
                    if arxiv_tag:
                        arxiv_link = arxiv_tag["href"]
            paper_info["arxiv_link"] = arxiv_link
            
            # 提取年份
            year_span = paper.find("span", itemprop="datePublished")
            paper_year = year_span.get_text(strip=True) if year_span else ""
            paper_info["year"] = paper_year
            
            # 根据年份过滤论文
            if str(year) == paper_year:
                result.append(paper_info)

    # 保存到 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "scientist": scientist,
            "profile_url": profile_url,
            "papers": result
        }, f, ensure_ascii=False, indent=2)

    print(f"数据已保存至 {os.path.abspath(output_file)}")

# 示例调用：
if __name__ == "__main__":
    download_papers("Feng Zhao", 2021, "dblp_papers.json")