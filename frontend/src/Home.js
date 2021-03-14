import React from 'react';
import { Layout, Menu, Breadcrumb } from 'antd';
import {
  DesktopOutlined,
  PieChartOutlined,
  FileOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import './Home.css';
import 'antd/dist/antd.css';

const { Header, Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;

export default class Home extends React.Component {
  state = {
    collapsed: false,
  };

  onCollapse = collapsed => {
    console.log(collapsed);
    this.setState({ collapsed });
  };

  render() {
    const { collapsed } = this.state;
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Sider collapsible collapsed={collapsed} onCollapse={this.onCollapse}>
          <div className="logo" />
          <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline">
            {/*<Menu.Item key="2" icon={<DesktopOutlined />}>*/}
            {/*  Recipes*/}
            {/*</Menu.Item>*/}
            <SubMenu key="sub1" icon={<UserOutlined />} title="Recipes">
              {/* TODO add popular tags
              Hard coded for now*/}
              <Menu.Item key="3">Breakfast</Menu.Item>
              <Menu.Item key="4">Lunch</Menu.Item>
              <Menu.Item key="5">Dinner</Menu.Item>
            </SubMenu>
            <Menu.Item key="9" icon={<FileOutlined />}>
              About
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout className="site-layout">
          <Header className="site-layout-background" style={{ padding: 0 }} />
          <Content style={{ margin: '0 16px' }}>
            <Breadcrumb style={{ margin: '16px 0' }}>
              <Breadcrumb.Item>Recipes</Breadcrumb.Item>
              <Breadcrumb.Item>Breakfast</Breadcrumb.Item>
            </Breadcrumb>
            <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>
              Recipe List
            </div>
          </Content>
          <Footer style={{ textAlign: 'center' }}>Ant Design ©2018 Created by Ant UED</Footer>
        </Layout>
      </Layout>
    );
  }
}
